# -*- coding: utf-8 -*-
"""ML-SIRP-2024

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/ml-sirp-2024-c78b3d02-6f83-4adb-b86d-aefde3206b08.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20240225/auto/storage/goog4_request%26X-Goog-Date%3D20240225T132007Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D8f522eadd55c69dab542d242130c9affbd990c4bf76add8428c33611a5d7b6192f48f91374fda2a87929c09fa64e8a2b1efe5c23c3edfd102d08226caab9ed7124b42211519f8e44d9ce172915da8c9f768d21ae12b3c9df418a16732026d919e6acb3a93f3c3514102da0bc1dc04bcda592d25cc975d969e1b7f802a98f837842d23964540a2f3bdc952d528f56efb0ce034d6cb6ade1f74792dc9e74de0d7f012aecdaa710fe0ab875180849014d4285224ab65bb23204c260b94618c0a592b7e06d0b210c0ef01ace484b4748c8373defc1ceb79b1f0a3659136cae8c5f51b97e0cbe49a0b38a7402fdcc2847972f38680be1138d9f553c1193b7dbe9bcc4

# Readme
--------------------------------------

## Introduction

In this study, we analyze a dataset consisting of 90 distinct animal images. Our objective is to explore various classification tasks using this dataset. Initially, we will organize the data for one-vs-rest classification as binary classification, and addressing a 5-class classification challenge. To assess the efficacy of these two classification model, we will employ classification matrices for comprehensive evaluation.

## Classification Techniques

### One-vs-Rest Classification:
Initially, we organize the dataset to facilitate one-vs-rest classification. This approach involves training a separate classifier for each class while treating all other classes as a single class. Consequently, we iteratively train multiple classifiers, each distinguishing between one class and the rest.

### 5-Class Classification:
Finally, we address a more complex classification scenario involving five distinct classes. This setup requires the development of a classification model capable of accurately assigning each input image to one of the five predefined classes.

## Model
The dataset underwent analysis utilizing three distinct architectures: CustomNN with attention mechanism, MobileNet, and EfficientNet. Across all cases examined, the test accuracy consistently surpassed the remarkable threshold of 99.5%.

## Evaluation

To gauge the effectiveness of each classification model, we employ classification matrices. These matrices provide a comprehensive overview of the model's performance by presenting key metrics such as accuracy, and precision, recall, and F1-score can be calculated by using the printed confusion matrix for each class. By analyzing these metrics, we can identify the strengths and weaknesses of each classification approach, enabling informed decision-making regarding model selection and refinement.

-------------------------------------------
# Libraries

Used for Folder Structure
"""

import os
from PIL import Image
import shutil
import random

"""Used for DL and Visualisation"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

import torchvision
from torchvision import transforms

from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

"""# Folder Structure

Study of Image type and folder structure for further analysis
"""

# The folder is contained in this directory
animal_dir = "/kaggle/input/animal-image-dataset-90-different-animals/animals/animals"

len(os.listdir(animal_dir))

with open("/kaggle/input/animal-image-dataset-90-different-animals/name of the animals.txt", 'r') as f:
    animal_info = f.read()

print(animal_info.split())

len(animal_info.split())



animal_names = {}
animal_directories = os.listdir(animal_dir)

for animal_name in animal_directories:
    animal_path = os.path.join(animal_dir, animal_name)
    num_images = len(os.listdir(animal_path))
    animal_names[animal_name] = num_images

animal_names



image_path = "/kaggle/input/animal-image-dataset-90-different-animals/animals/animals/antelope/02f4b3be2d.jpg"
image = Image.open(image_path)
width, height = image.size
print(f"width: {width}, height: {height}")

"""# **One vs Rest Classification**

This dataset class retrieves all images from the folder at the `ith` index, as well as `10%` of the images from each of the other folders. This approach helps to conserve memory and end potential train and test problems arising from significant discrepancies in image numbers across folders.


```
Note: Earlier the dataset took `ith` folder (60) images, and (5340) images in the rest folder, but this caused errors so, in the final version of the code this issue was solved using this method.
```
"""

path = "/kaggle/input/animal-image-dataset-90-different-animals/animals/animals"

"""In the transform, the mean is ```mean=[0.485, 0.456, 0.406]``` and ```std=[0.229, 0.224, 0.225]``` to normalize images because it is given by PyTorch by default and is the Imagenet default values and in practice it is assumed to work better then rest values.

The label is 0 and 1.
"""

class dataset_new(torch.utils.data.Dataset):
    def __init__(self,data_idx,take=0.1,path=path):
        super().__init__()
        classes = os.listdir(path)
        folder_name = classes[data_idx]
        self.images = []
        self.labels = []
        self.transforms = transforms.Compose([
            transforms.Resize(256), # 256 for efficient net , 224
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        for folder in classes:
            if folder==folder_name:
                limit = 1
            else:
                limit = take
            anim_fold = os.path.join(path, folder)
            for l,localpath in enumerate(os.listdir(anim_fold)):
                if(l>=limit*len(os.listdir(anim_fold))):
                    break
                img_path = os.path.join(anim_fold, localpath)
                self.images.append(img_path)
                if folder==folder_name:
                    self.labels.append(1)
                else:
                    self.labels.append(0)

    def __len__(self):
        return len(self.images)
    def __getitem__(self,idx):
        img = Image.open(self.images[idx])
        label = self.labels[idx]
        return self.transforms(img), torch.tensor(label,dtype=torch.long)





"""```run_label_classification_one_vs_rest_fold```, this function is the main structure, and works to run the model using different models and perform calcualtions. It does 3fold CV with 3 epochs each using one_vs_rest and displays the test and train, accuracy and loss value after each epoch and also saves the plot."""

def run_label_classification_one_vs_rest_fold(model_net, name):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    name_model = str(name)
    for i in range(90):
        print(animal_info.split()[i])
        dataset = dataset_new(i)

        kfold = KFold(n_splits=3, shuffle=True)

        print('--------------------------------')

        for fold, (train_ids, test_ids) in enumerate(kfold.split(dataset)):

            print(f'FOLD {fold}')
            print('--------------------------------')

            train_subsampler = torch.utils.data.SubsetRandomSampler(train_ids)
            test_subsampler = torch.utils.data.SubsetRandomSampler(test_ids)

            train_loader = DataLoader(dataset, batch_size=32, sampler=train_subsampler, pin_memory=True, num_workers=2)
            test_loader = DataLoader(dataset, batch_size=32, sampler=test_subsampler, pin_memory=True, num_workers=2)

            model = model_net
            model.to(device)

            optimizer = optim.Adam(model.parameters(), lr=5e-5)
            train_losses = []
            test_losses = []
            train_accuracies = []
            test_accuracies = []

            for epoch in range(3):

                model.train()
                correct = 0
                total = 0
                train_loss = 0.0
                for _, (inputs, labels) in enumerate(train_loader):
                    inputs, labels = inputs.to(device), labels.to(device)
                    optimizer.zero_grad()

                    outputs = model(inputs)
                    loss = nn.CrossEntropyLoss()(outputs, labels)
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item()
                    _, predicted = outputs.max(1)
                    total += labels.size(0)
                    correct += predicted.eq(labels).sum().item()

                model.eval()
                test_loss = 0.0
                test_correct = 0
                test_total = 0
                all_labels = []
                all_predictions = []

                for inputs, labels in test_loader:
                    inputs, labels = inputs.to(device), labels.to(device)
                    outputs = model(inputs)
                    loss = nn.CrossEntropyLoss()(outputs, labels)
                    test_loss += loss.item()*inputs.size(0)
                    _, predicted = outputs.max(1)
                    test_total += labels.size(0)
                    test_correct += predicted.eq(labels).sum().item()
                    all_labels.extend(labels.cpu().numpy())
                    all_predictions.extend(predicted.cpu().numpy())


                test_loss = test_loss / len(test_loader)
                train_loss = train_loss/len(train_loader)
                test_accuracy = 100.0 * correct / total
                train_accuracy = 100.0 * test_correct/test_total

                train_losses.append(train_loss)
                test_losses.append(test_loss)
                train_accuracies.append(train_accuracy)
                test_accuracies.append(test_accuracy)

                print('Epoch: {} \tTraining Loss: {:.6f} \tTest Loss: {:.6f} \tTrain Accuracy {:.6f}% \tTest Accuracy: {:.2f}%'.format(
                    epoch+1,
                    train_loss,
                    test_loss,
                    train_accuracy,
                    test_accuracy
                    ))

            directory = f'/kaggle/working/one-vs-rest/{name}/{animal_info.split()[i]}/'
            os.makedirs(directory, exist_ok=True)

            plt.figure(figsize=(10, 5))
            plt.plot(train_accuracies, label='Train Accuracy')
            plt.plot(test_accuracies, label='Test Accuracy')
            plt.title('Accuracy Curve for Dataset Name: {} Fold {}'.format(animal_info.split()[i], fold))
            plt.xlabel('Epoch')
            plt.ylabel('Accuracy')
            plt.savefig(os.path.join(directory, f'{fold}.png'))


            print('Confusion Matrix for fold {}'.format(fold))
            print(confusion_matrix(all_labels, all_predictions))



"""Model using Efficientnet b0"""

!pip install efficientnet_pytorch



from efficientnet_pytorch import EfficientNet

class CEfficientNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.efficientnet = EfficientNet.from_pretrained('efficientnet-b0')
        self.fc = nn.Linear(1000, 2)

    def forward(self, x):
        x = self.efficientnet(x)
        x = self.fc(x)
        return x

model_EfficientNet = CEfficientNet()
run_label_classification_one_vs_rest_fold(model_EfficientNet, 'Effnet')



"""Model using MobileNet"""

from torchvision import models

class CMobileNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.mobilenet = models.mobilenet_v2(pretrained=True)
        self.fc = nn.Linear(1000, 2)

    def forward(self, x):
        x = self.mobilenet(x)
        x = self.fc(x)
        return x

model_MobileNet = CMobileNet()
run_label_classification_one_vs_rest_fold(model_MobileNet, 'Mobilenet')

"""Model using CustomNet"""

class Attention(nn.Module):
    def __init__(self, in_features):
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(in_features, in_features),
            nn.Tanh(),
            nn.Linear(in_features, 1),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        attention_weights = self.attention(x)
        return attention_weights * x

class CustomCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64*56*56, 1000)
        self.attention = Attention(1000)
        self.fc2 = nn.Linear(1000, 2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.attention(x)
        x = self.fc2(x)
        return x

model_CustomCNN = CustomCNN()
run_label_classification_one_vs_rest_fold(model_CustomCNN, 'CustomCNN')

"""# 5 Class Classification using 3 Fold CV"""

path = "/kaggle/input/animal-image-dataset-90-different-animals/animals/animals"

class dataset_pent_class(torch.utils.data.Dataset):
    def __init__(self,start_idx, path=path, window_size= 5):
        super().__init__()
        classes = os.listdir(path)
        self.images = []
        self.labels = []
        self.transforms = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        end_idx = start_idx*5 + window_size
        for i in range(start_idx*5, end_idx):
            folder_name = classes[i]
            anim_fold = os.path.join(path, folder_name)
            for localpath in os.listdir(anim_fold):
                img_path = os.path.join(anim_fold, localpath)
                self.images.append(img_path)
                self.labels.append(i % window_size)

    def __len__(self):
        return len(self.images)
    def __getitem__(self,idx):
        img = Image.open(self.images[idx])
        label = self.labels[idx]
        return self.transforms(img), torch.tensor(label, dtype=torch.long)

"""```run_label_classification_one_vs_rest_fold``` even though the method name is the same, this takes multiple inputs, and saves the model weights. These weights are then loaded to visualise the model view images after the full process."""

def run_label_classification_one_vs_rest_fold(model_net, name, start_idx=0, window_size=5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    name_model = str(name)
    for i in range(start_idx, 17, window_size):
        print(i, "structure folder")
        dataset = dataset_pent_class(i, window_size=window_size)

        kfold = KFold(n_splits=3, shuffle=True)

        print('--------------------------------')

        for fold, (train_ids, test_ids) in enumerate(kfold.split(dataset)):

            print(f'FOLD {fold}')
            print('--------------------------------')

            train_subsampler = torch.utils.data.SubsetRandomSampler(train_ids)
            test_subsampler = torch.utils.data.SubsetRandomSampler(test_ids)

            train_loader = DataLoader(dataset, batch_size=32, sampler=train_subsampler, pin_memory=True, num_workers=2)
            test_loader = DataLoader(dataset, batch_size=32, sampler=test_subsampler, pin_memory=True, num_workers=2)

            model = model_net
            model.to(device)

            optimizer = optim.Adam(model.parameters(), lr=5e-5)
            train_losses = []
            test_losses = []
            train_accuracies = []
            test_accuracies = []

            for epoch in range(3):

                model.train()
                correct = 0
                total = 0
                train_loss = 0.0
                for _, (inputs, labels) in enumerate(train_loader):
                    inputs, labels = inputs.to(device), labels.to(device)
                    optimizer.zero_grad()

                    outputs = model(inputs)
                    loss = nn.CrossEntropyLoss()(outputs, labels)
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item()
                    _, predicted = outputs.max(1)
                    total += labels.size(0)
                    correct += predicted.eq(labels).sum().item()

                model.eval()
                test_loss = 0.0
                test_correct = 0
                test_total = 0
                all_labels = []
                all_predictions = []

                for inputs, labels in test_loader:
                    inputs, labels = inputs.to(device), labels.to(device)
                    outputs = model(inputs)
                    loss = nn.CrossEntropyLoss()(outputs, labels)
                    test_loss += loss.item()*inputs.size(0)
                    _, predicted = outputs.max(1)
                    test_total += labels.size(0)
                    test_correct += predicted.eq(labels).sum().item()
                    all_labels.extend(labels.cpu().numpy())
                    all_predictions.extend(predicted.cpu().numpy())


                test_loss = test_loss / len(test_loader)
                train_loss = train_loss/len(train_loader)
                test_accuracy = 100.0 * correct / total
                train_accuracy = 100.0 * test_correct/test_total

                train_losses.append(train_loss)
                test_losses.append(test_loss)
                train_accuracies.append(train_accuracy)
                test_accuracies.append(test_accuracy)

                print('Epoch: {} \tTraining Loss: {:.6f} \tTest Loss: {:.6f} \tTrain Accuracy {:.6f}% \tTest Accuracy: {:.2f}%'.format(
                    epoch+1,
                    train_loss,
                    test_loss,
                    train_accuracy,
                    test_accuracy
                    ))

            directory = f'/kaggle/working/5fold/{i}/{fold}/'
            os.makedirs(directory, exist_ok=True)

            plt.figure(figsize=(10, 5))
            plt.plot(train_accuracies, label='Train Accuracy')
            plt.plot(test_accuracies, label='Test Accuracy')
            plt.title('Accuracy Curve for {} Dataset, Fold {}'.format(i, fold))
            plt.xlabel('Epoch')
            plt.ylabel('Accuracy')
            plt.savefig(os.path.join(directory, f'{fold}.png'))

            model_directory = f'/kaggle/working/5fold_model/'
            os.makedirs(model_directory, exist_ok=True)
            torch.save(model.state_dict(), os.path.join(model_directory, f'{name_model}.pth'))


            print('Confusion Matrix for fold {}'.format(fold))
            print(confusion_matrix(all_labels, all_predictions))

"""EfficientNet b0

"""

!pip install efficientnet_pytorch

from efficientnet_pytorch import EfficientNet

class CEfficientNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.efficientnet = EfficientNet.from_pretrained('efficientnet-b0')
        self.fc = nn.Linear(1000, 5)

    def forward(self, x):
        x = self.efficientnet(x)
        x = self.fc(x)
        return x

model_EfficientNet = CEfficientNet()
run_label_classification_one_vs_rest_fold(model_EfficientNet, 'EffNet', 0, 5)



"""MobileNet"""

from torchvision import models

class CMobileNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.mobilenet = models.mobilenet_v2(pretrained=True)
        self.fc = nn.Linear(1000, 5)

    def forward(self, x):
        x = self.mobilenet(x)
        x = self.fc(x)
        return x

model_MobileNet = CMobileNet()
run_label_classification_one_vs_rest_fold(model_MobileNet, 'MobileNet', 0, 5)



"""Custom NeuralNetwork"""

class Attention(nn.Module):
    def __init__(self, in_features):
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(in_features, in_features),
            nn.Tanh(),
            nn.Linear(in_features, 1),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        attention_weights = self.attention(x)
        return attention_weights * x

class CustomCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64*56*56, 1000)
        self.attention = Attention(1000)
        self.fc2 = nn.Linear(1000, 5)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.attention(x)
        x = self.fc2(x)
        return x

model_CustomCNN = CustomCNN()
run_label_classification_one_vs_rest_fold(model_CustomCNN, 'CustomCNN', 0, 5)



"""# Model Visualisation"""

import torchvision
from torchvision import models, transforms, utils
from torch.autograd import Variable
import scipy.misc
import json

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

"""Using the same transform as used during dataloading

Plotting the output of all convolutional layers and discuss the insights on automatically created features.
"""

#Taking an Image
image = Image.open(str('/kaggle/input/animal-image-dataset-90-different-animals/animals/animals/antelope/02f4b3be2d.jpg'))
plt.imshow(image)

"""# Function for Visual

"""

transforms = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

def nn_layer_visual(image, model, model_path):

        model.load_state_dict(torch.load(model_path))


        model_weights =[]
        conv_layers = []
        model_children = list(model.children())
        counter = 0
        for i in range(len(model_children)):
            if type(model_children[i]) == nn.Conv2d:
                counter+=1
                model_weights.append(model_children[i].weight)
                conv_layers.append(model_children[i])
            elif type(model_children[i]) == nn.Sequential:
                for j in range(len(model_children[i])):
                    for child in model_children[i][j].children():
                        if type(child) == nn.Conv2d:
                            counter+=1
                            model_weights.append(child.weight)
                            conv_layers.append(child)
        print(f"Total convolution layers: {counter}")
        print("conv_layers")

        image = transforms(image)
        print(f"Image shape before: {image.shape}")
        image = image.unsqueeze(0)
        print(f"Image shape after: {image.shape}")

        if len(image.shape) == 3:
            image = image.unsqueeze(0)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        image = image.to(device)

        print(f"Image shape before: {image.shape}")

        outputs = []
        names = []
        for layer in conv_layers[0:]:
            image = layer(image)
            outputs.append(image)
            names.append(str(layer))

        print(len(outputs))
        for feature_map in outputs:
            print(feature_map.shape)

        processed = []
        for feature_map in outputs:
            feature_map = feature_map.squeeze(0)
            gray_scale = torch.sum(feature_map,0)
            gray_scale = gray_scale / feature_map.shape[0]
            processed.append(gray_scale.data.cpu().numpy())
        for fm in processed:
            print(fm.shape)

        fig = plt.figure(figsize=(30, 50))
        for i in range(len(processed)):
            a = fig.add_subplot(5, 4, i+1)
            imgplot = plt.imshow(processed[i])
            a.axis("off")
            a.set_title(names[i].split('(')[0], fontsize=30)

"""# Custom CNN Visual"""

nn_layer_visual(image, model_CustomCNN, '/kaggle/working/5fold_model/CustomCNN.pth')




