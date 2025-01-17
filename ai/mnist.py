import io
from os.path import join

import torch
from PIL import Image
from torch import nn
from torch import optim
from torch.nn import functional as func
from torch.optim.lr_scheduler import StepLR
from torchvision import datasets, transforms

MODEL_PATH = join("data", "mnist_cnn.pt")


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = func.relu(x)
        x = self.conv2(x)
        x = func.relu(x)
        x = func.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = func.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = func.log_softmax(x, dim=1)
        return output


def train(model, device, train_loader, optimizer, epoch, dry_run, log_interval):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = func.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                       100. * batch_idx / len(train_loader), loss.item()))
            if dry_run:
                break


def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += func.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))


def train_and_save_model(batch_size: int = 64,
                         test_batch_size: int = 1000,
                         epochs: int = 14,
                         learning_rate: float = 1.,
                         gamma: float = .7,
                         no_cuda: bool = False,
                         no_mps: bool = False,
                         dry_run: bool = False,
                         seed: int = 1,
                         log_interval: int = 10,
                         save_model: bool = False):
    """
    @param batch_size: input batch size for training (default: 64)
    @param test_batch_size: input batch size for testing (default: 1000)
    @param epochs: number of epochs to train (default: 14)
    @param learning_rate: learning rate (default: 1.0)
    @param gamma: Learning rate step gamma (default: 0.7)
    @param no_cuda: disables CUDA training
    @param no_mps: disables macOS GPU training
    @param dry_run: quickly check a single pass
    @param seed: random seed (default: 1)
    @param log_interval: how many batches to wait before logging training status
    @param save_model: For Saving the current Model
    """

    use_cuda = not no_cuda and torch.cuda.is_available()
    use_mps = not no_mps and torch.backends.mps.is_available()

    torch.manual_seed(seed)

    if use_cuda:
        print("Using cuda")
        device = torch.device("cuda")
    elif use_mps:
        print("Using mps")
        device = torch.device("mps")
    else:
        print("Using cpu")
        device = torch.device("cpu")

    train_kwargs = {'batch_size': batch_size}
    test_kwargs = {'batch_size': test_batch_size}
    if use_cuda:
        cuda_kwargs = {'num_workers': 1,
                       'pin_memory': True,
                       'shuffle': True}
        train_kwargs.update(cuda_kwargs)
        test_kwargs.update(cuda_kwargs)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    dataset1 = datasets.MNIST('data', train=True, download=True, transform=transform)
    dataset2 = datasets.MNIST('data', train=False, transform=transform)
    train_loader = torch.utils.data.DataLoader(dataset1, **train_kwargs)
    test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)

    model = Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=learning_rate)

    scheduler = StepLR(optimizer, step_size=1, gamma=gamma)
    for epoch in range(1, epochs + 1):
        train(model, device, train_loader, optimizer, epoch, dry_run, log_interval)
        test(model, device, test_loader)
        scheduler.step()

    if save_model:
        torch.save(model.state_dict(), MODEL_PATH)


def transform_image(image_bytes):
    # transform = transforms.Compose([
    #     transforms.Grayscale(),
    #     transforms.Resize((28, 28)),
    #     transforms.ToTensor(),
    #     transforms.Normalize((0.1307,), (0.3081,))
    # ])
    # return transform(white_image).unsqueeze(0)
    image = Image.open(io.BytesIO(image_bytes))
    white_image = Image.new("RGBA", image.size, (255, 255, 255))
    white_image.paste(image, mask=image)

    gray = transforms.Grayscale()(white_image)
    scaled = transforms.Resize((28, 28))(gray)
    tensor = transforms.ToTensor()(scaled)
    normalized = transforms.Normalize((0.1307,), (0.3081,))(tensor)
    return normalized.unsqueeze(0)


def get_prediction(image_tensor):
    model = Net()
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()

    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted = outputs.max(1)
        return predicted.item()


def run_model(img_bytes: bytes):
    img_tensor = transform_image(img_bytes)
    return get_prediction(img_tensor)

    # Run inference with input of size [64, 1, 28, 28]
    # 64: batch size
    # 1: # of channels (1 for greyscale images)
    # (28, 28): input image size
    # return model(tensor)


if __name__ == '__main__':
    train_and_save_model(save_model=True)
