
from mxnet import ndarray as nd
from mxnet import autograd
import matplotlib.pyplot as plt
import random

# data set
num_inputs = 2
num_examples = 1000

true_w = [2, -3.4]
true_b = 4.2

X = nd.random_normal(shape=(num_examples, num_inputs))
y = true_w[0] * X[:, 0] + true_w[1] * X[:, 1] + true_b
y += .01 * nd.random_normal(shape=y.shape)

plt.scatter(X[:, 0].asnumpy(), y.asnumpy())
plt.show()

# generate random training data set
batch_size = 10
def data_iter():
    idx = list(range(num_examples))
    random.shuffle(idx)
    for i in range(0, num_examples, batch_size):
        j = nd.array(idx[i: min(i+batch_size, num_examples)])
        yield nd.take(X, j), nd.take(y, j)

for data, label in data_iter():
    print(data, label)
    break

# initial model params
w = nd.random_normal(shape=(num_inputs, 1))
b = nd.zeros((1,))
params = [w, b]

for param in params:
    param.attach_grad()

# define regression model
def net(X):
    return nd.dot(X, w) + b

# define loss function
def square_loss(yhat, y):
    return (yhat - y.reshape(yhat.shape)) ** 2

# define optimization algo: Stochastic gredient descent
def SGD(params, lr):
    for param in params:
        param[:] = param - lr * param.grad

# training model

## model function
def real_fn(X):
    return true_w[0] * X[:, 0] + true_w[1] * X[:, 1] + true_b

## drawing Loss during training, Estimated vs real function
def plot(losses, X, sample_size=100):
    xs = list(range(len(losses)))
    f, (fg1, fg2) = plt.subplots(1, 2)
    fg1.set_title('Loss during training')
    fg1.plot(xs, losses, '-r')
    fg2.set_title('Estimated vs real function')
    fg2.plot(X[:sample_size, 1].asnumpy(),
             net(X[:sample_size, :]).asnumpy(), 'or', label='Estimated')
    fg2.plot(X[:sample_size, 1].asnumpy(),
             real_fn(X[:sample_size, :]).asnumpy(), '*g', label='Real')
    fg2.legend()
    plt.show()

epochs = 5
learning_rate = .001
niter = 0
losses = []
moving_loss = 0
smoothing_constant = .01

## training
for e in range(epochs):
    total_loss = 0

    for data, label in data_iter():
        with autograd.record():
            output = net(data)
            loss = square_loss(output, label)
        loss.backward()
        SGD(params, learning_rate)
        total_loss += nd.sum(loss).asscalar()

        niter +=1
        curr_loss = nd.mean(loss).asscalar()
        moving_loss = (1 - smoothing_constant) * moving_loss + (smoothing_constant) * curr_loss

        # correct the bias from the moving averages
        est_loss = moving_loss/(1-(1-smoothing_constant)**niter)

        if (niter + 1) % 100 == 0:
            losses.append(est_loss)
            print("Epoch %s, batch %s. Moving avg of loss: %s. Average loss: %f" % (e, niter, est_loss, total_loss/num_examples))
            plot(losses, X)

# print training params with real params
print("true_w: %s, trainned_w: %s " % (true_w, w))
print("true_b: %s, trainned_b: %s " % (true_b, b))

