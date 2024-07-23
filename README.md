# NN-webui

Web server that provides a web interface for interacting with an MNIST-trained neural network

## Installation

### On *NIX systems

```bash
# Create virtual environment
python3 -m venv .env
# Activate it
source .env/bin/activate
# Install dependencies
python3 -m pip install -r requirements.txt
 
# Train MNIST model
python3 ai/mnist.py
```

### On Windows systems

```batch
:: Create virtual environment
python -m venv .env
:: Activate it
.env\Scripts\activate
:: Install dependencies
python -m pip install -r requirements.txt
 
:: Train MNIST model
python ai\mnist.py
```

To train the model using hardware, follow [PyTorch documentation](https://pytorch.org/get-started/locally/)

## Running the application

```bash
python -m flask run
```
