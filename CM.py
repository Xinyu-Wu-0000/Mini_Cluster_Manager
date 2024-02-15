from email.policy import default
import json
import click
from cluster_manager import ClusterManager


@click.group()
def cli():
    pass


@cli.command()
@click.argument("number", type=click.INT)
def create(number):
    """Create a certain number of containers"""
    res = CM.create(number)
    click.echo(f"created {number} containers")
    for idx, con in enumerate(res):
        print("container", idx + 1, ":", con)


@cli.command()
def list():
    """List all containers"""
    res = CM.list_all()
    click.echo(f"There are {res.__len__()} containers:")
    for idx, con in enumerate(res):
        print("container", idx + 1, ":", con)


@cli.command()
@click.option('--name', help="name of the container to delete, delete all if empty", type=click.STRING, default="")
def delete(name):
    """Delete containers, you can delete all containers or a specific one by name
        Running containers will not be deleted
    """
    res = CM.delete_con(name)
    if isinstance(res, type([])):
        if len(res) == 0:
            print("There are no not running containers to delete!")
        else:
            print(f"deleted all not running containers: {res}")
    elif res == -1:
        print(f"no container names {name}")
    elif res == 0:
        print(f"container {name} is running, please stop it before delete it!")
    else:
        print(f"deleted container {res}")


@cli.command()
@click.option('--name', help="name of the container to stop, stop all if empty", type=click.STRING, default="")
def stop(name):
    """Stop containers, you can stop all containers or a specific one by name"""
    res = CM.stop_con(name)
    if isinstance(res, type([])):
        if len(res) == 0:
            print("There are no running containers to stop!")
        else:
            print(f"stopped all running containers: {res}")
    elif res == -1:
        print(f"no container names {name}")
    elif res == 0:
        print(f"container {name} is not running")
    else:
        print(f"stopped container {res}")


@cli.command()
@click.option("--name", help="the name of container to run the command, empty for creating a new container to run the command",
              type=click.STRING, default="")
@click.option("--cmd", help="the command to run",
              type=click.STRING, default="")
def run(name, cmd):
    """Run a cmd in a container, without giving a name of a specific container, a new container will be created"""
    res = CM.run_cmd(name, cmd)
    if isinstance(res, type(0)) and res == -1:
        print(f"no container name {name}")
    else:
        print("command output:")
        print(res, end="")


@cli.command()
def task2():
    """This is a parallel data processing task in which 4 containers will execute asynchronously"""
    res = CM.task2()
    res.sort(key=lambda x: x["container index"])
    for data in res:
        print("result from container", data["container index"] + 1, ":", data)


@cli.command()
def task3():
    """This is a linear regression implemented in Pytorch"""
    res = CM.task3()
    print(res, end="")


@cli.result_callback()
def log_state(result, **kwargs):
    with open(".state.json", "w") as fp:
        CM.list_all()
        state = [con.attrs for con in CM.cons]
        json.dump(state, fp)


if __name__ == "__main__":
    CM = ClusterManager()
    cli()
