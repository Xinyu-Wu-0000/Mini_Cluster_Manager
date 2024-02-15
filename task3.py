import numpy
import torch
import argparse
from torch.autograd import Variable
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Client for Task 2')
parser.add_argument('--file', type=str,
                    help='file path of data')
args = parser.parse_args()


data = torch.load(args.file)

data_size = 100000
x_data = Variable(data["x_data"])
y_data = Variable(data["y_data"])


class LinearRegressionModel(torch.nn.Module):

    def __init__(self):
        super(LinearRegressionModel, self).__init__()
        self.linear = torch.nn.Linear(1, 1)  # One in and one out

    def forward(self, x):
        y_pred = self.linear(x)
        return y_pred


# our model
our_model = LinearRegressionModel()

criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(our_model.parameters(), lr=0.01)
loss_log = []
for epoch in range(1000):

    # Forward pass: Compute predicted y by passing
    # x to the model
    divide_num = 100
    rand_batch = numpy.random.randint(
        0, high=data_size, size=(int(data_size / divide_num)))

    pred_y = our_model(x_data[rand_batch])
    real_y = y_data[rand_batch]
    # Compute and print loss
    loss = criterion(pred_y, real_y)

    # Zero gradients, perform a backward pass,
    # and update the weights.
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    loss_log.append(loss.item())
    if (epoch + 1) % 100 == 0 or epoch < 10:
        print('epoch {}, loss {}'.format(epoch + 1, loss.item()))

divide_num = 1000
rand_batch = numpy.random.randint(
    0, high=data_size, size=(int(data_size / divide_num)))
plt.plot(loss_log)
plt.title("Training log")
plt.xlabel("epoch")
plt.ylabel("loss")
plt.tight_layout()
plt.savefig("data/train.png", dpi=300)
print("saved training log to ./data/train.png")
plt.cla()
plt.scatter(x_data[rand_batch], y_data[rand_batch])
plt.plot(x_data.reshape(data_size)[rand_batch], our_model(
    x_data).detach().reshape(data_size)[rand_batch],
    color="g")
plt.title("Result")
plt.xlabel("x")
plt.ylabel("y")
plt.tight_layout()
plt.savefig("data/result.png", dpi=300)
print("saved result to ./data/result.png")
