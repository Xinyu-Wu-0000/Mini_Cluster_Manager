import json
import os
import asyncio
import docker
import numpy
import torch


class ClusterManager():
    def __init__(self) -> None:
        self.data_path = "data"
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
        self.workdir = "/usr/src/app/"
        self.image_name = "my_task_image"
        self.name_prefix = "my_task_container"
        self.cli = docker.client.from_env()
        self.containers = []  # 'CONTAINER ID', 'IMAGE', 'CREATED', 'STATUS', 'NAME'
        self.cons = []
        self.list_all()

    def create(self, n):
        self.list_all()
        res = []
        vollumes = {os.path.abspath(self.data_path): {
            'bind': self.workdir + self.data_path, 'mode': 'rw'}}
        for idx in range(n):
            free_name = 0
            for i in range(100000):
                name = self.name_prefix + "_" + str(i)
                if self.search_by_name(self.containers, name) == -1:
                    free_name = name
                    break
            con = self.cli.containers.create(
                self.image_name,
                volumes=vollumes,
                name=free_name,
                tty=True)
            self.cli.api.stop(con.attrs["Id"])
            self.list_all()
            self.append_con(res, con)
        return [con["NAME"] for con in res]

    def remove_single(self, id: str):
        con = self.cli.containers.get(id)
        if con.attrs["State"]["Status"] == "running":
            return -1
        self.cli.api.remove_container(con.attrs["Id"])
        return 1

    def delete_con(self, name: str):
        self.list_all()
        if name == "":
            res = []
            for con in self.cons:
                remove_code = self.remove_single(con.attrs["Id"])
                if remove_code == 1:
                    idx = self.search_by_id(self.containers, con.attrs["Id"])
                    res.append(self.containers[idx]["NAME"])
            return res
        idx = self.search_by_name(self.containers, name)
        if idx == -1:
            return -1
        remove_code = self.remove_single(self.containers[idx]["CONTAINER ID"])
        if remove_code == 1:
            return self.containers[idx]["NAME"]
        else:
            return 0

    def stop_single(self, id: str):
        con = self.cli.containers.get(id)
        if con.attrs["State"]["Status"] != "running":
            return -1
        self.cli.api.stop(con.attrs["Id"])
        return 1

    def stop_con(self, name: str):
        self.list_all()
        if name == "":
            res = []
            for con in self.cons:
                remove_code = self.stop_single(con.attrs["Id"])
                if remove_code == 1:
                    idx = self.search_by_id(self.containers, con.attrs["Id"])
                    res.append(self.containers[idx]["NAME"])
            return res
        idx = self.search_by_name(self.containers, name)
        if idx == -1:
            return -1
        remove_code = self.stop_single(self.containers[idx]["CONTAINER ID"])
        if remove_code == 1:
            return self.containers[idx]["NAME"]
        else:
            return 0

    def list_all(self):
        self.containers.clear()
        self.cons.clear()
        cons = self.cli.containers.list(all=True)
        for con in cons:
            res = self.append_con(self.containers, con)
            if res == 1:
                self.cons.append(con)
        return self.containers

    def append_con(self, data: list, container):
        if self.search_by_name(data, container.attrs["Name"]) != -1:
            return -1
        if not container.attrs["Name"].startswith("/" + self.name_prefix):
            return -1
        data.append({
            "NAME": container.attrs["Name"][1:],
            "IMAGE": container.attrs["Image"],
            "STATUS": container.attrs["State"]["Status"],
            "CREATED": container.attrs["Created"],
            "CONTAINER ID": container.attrs["Id"],
        })
        return 1

    def search_by_id(self, data: list, id: str):
        for idx, con in enumerate(data):
            if con["CONTAINER ID"] == id:
                return idx
        return -1

    def search_by_name(self, data: list, name: str):
        for idx, con in enumerate(data):
            if con["NAME"] == name:
                return idx
        return -1

    def run_cmd(self, name: str, cmd: str):
        self.list_all()
        if name == "":
            res = self.create(1)
            name = res[0]
            self.list_all()
        idx = self.search_by_name(self.containers, name)
        if idx == -1:
            return -1
        con = self.cli.containers.get(self.containers[idx]["CONTAINER ID"])
        self.cli.api.start(con.attrs["Id"])
        ids = self.cli.api.exec_create(con.attrs["Id"], cmd=cmd)
        res = self.cli.api.exec_start(ids, tty=True)
        return res.decode()

    def raw_run(self, id: str, cmd: str):
        self.cli.api.start(id)
        ids = self.cli.api.exec_create(id, cmd=cmd)
        res = self.cli.api.exec_start(ids, tty=True)
        return res.decode()

    async def async_task2(self, ids: list, csv_path: str):
        loop = asyncio.get_event_loop()
        tasks = []
        for i in range(4):
            tasks.append(loop.run_in_executor(None,
                                              self.raw_run,
                                              ids[i],
                                              f"python task2.py --file {csv_path} --idx {i}"))
        tasks_res = await asyncio.gather(*tasks)
        return tasks_res

    def task2(self):
        data = numpy.random.random(100000)
        csv_path = self.data_path + "/data.csv"
        numpy.savetxt(csv_path, data, delimiter=',')
        cons = self.create(4)
        self.list_all()
        ids = []
        for con in cons:
            idx = self.search_by_name(self.containers, con)
            ids.append(self.containers[idx]["CONTAINER ID"])
        res = asyncio.get_event_loop().run_until_complete(self.async_task2(ids, csv_path))
        return [json.loads(data) for data in res]

    def task3(self):
        data_size = 100000
        x_data = torch.linspace(0, 10, data_size)
        y_data = torch.linspace(0, 10, data_size)
        y_data = y_data * ((torch.rand(data_size) - 0.5) / 5 + 1) + \
            ((torch.rand(data_size) - 0.5) / 2)
        torch.save({"x_data": x_data.reshape(data_size, 1),
                    "y_data": y_data.reshape(data_size, 1)},
                   "data/data.ptd")
        res = self.run_cmd("", "python task3.py --file \"data/data.ptd\"")
        return res
