# -*- coding: utf-8 -*-
"""CS6910_assignment-2Bipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1w8GXLjspkRASLv4i9dfYWetm2MXnKMA_
"""

import os
import numpy as np
import torch
import glob
import torch.nn as nn
from torchvision.transforms import transforms
from torch.utils.data import DataLoader
from torch.autograd import Variable
import torchvision
import pathlib
import matplotlib.pyplot as plt
from torch.utils.data.sampler import SubsetRandomSampler
from torchvision import datasets
import torch.nn.init
import torch.optim as optim

!pip install wandb -qqq
import wandb

!wandb login --relogin
entity_name="siddharth-s"

project_name="FODL_Assignment_2A"

!wget https://storage.googleapis.com/wandb_datasets/nature_12K.zip

!unzip /content/nature_12K.zip

class prepare_data():

  def __init__(self,augment=True,batch_size=32):
    self.train_path='/content/inaturalist_12K/train'
    self.test_path='/content/inaturalist_12K/val'
    self.augment=augment
    self.batch_size=batch_size

  def prepare(self,):
    if self.augment==True:
       train_transforms = transforms.Compose([transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.RandomRotation((120)),
            transforms.RandomApply(torch.nn.ModuleList([transforms.ColorJitter()]), p=0.5),
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

       test_transforms = transforms.Compose([transforms.RandomRotation(120),
                                      transforms.Resize((224,224)),
                                      transforms.ToTensor(),
                                      transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    else:
       train_transforms = transforms.Compose([transforms.Resize((224,224)),
                                       transforms.ToTensor(),                               
                                       transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

       test_transforms = transforms.Compose([transforms.Resize((224,224)),
                                      transforms.ToTensor(),
                                      transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])


    train_data = datasets.ImageFolder(self.train_path, transform=train_transforms) 
    test_data = datasets.ImageFolder(self.test_path, transform=test_transforms)

    num_workers = 0
    valid_size = 0.2
    num_train = len(train_data)
    indices = list(range(num_train))
    num_train_class=1000
    split = int(np.floor(valid_size * num_train_class))
    train_id=[]
    valid_id=[]
    for i in range(10):
      x=i+1
      train_idx, valid_idx = indices[i*1000+split:x*1000], indices[i*1000:i*1000+split]
      train_id=train_id+train_idx
      valid_id=valid_id+valid_idx

    train_sampler = SubsetRandomSampler(train_id)
    valid_sampler = SubsetRandomSampler(valid_id)

    train_loader = torch.utils.data.DataLoader(train_data, batch_size=self.batch_size,
    sampler=train_sampler, num_workers=num_workers)
    valid_loader = torch.utils.data.DataLoader(train_data, batch_size=self.batch_size, 
    sampler=valid_sampler, num_workers=num_workers)
    test_loader = torch.utils.data.DataLoader(test_data, batch_size=self.batch_size, 
    num_workers=num_workers)

    return train_loader,valid_loader,test_loader

from torchvision import models
import torch.nn as nn
def tl_Resnet50():
  device = 'cuda' if torch.cuda.is_available() else 'cpu'
  model= models.resnet50(pretrained=True).to(device)

  for param in model.parameters():
    param.requires_grad = False   

  n_inputs = model.fc.in_features 
  model.fc = nn.Sequential(
               nn.Linear(n_inputs, 2048),
               nn.ReLU(inplace=True),
               nn.Dropout(0.3),
               nn.Linear(2048, 10))
  return model

def train_resnet():

  device = 'cuda' if torch.cuda.is_available() else 'cpu'
  model=tl_Resnet50().to(device)
  optimizer = optim.Adam(model.parameters(),lr=1e-3)
  criterion = nn.CrossEntropyLoss().to(device)
  
  data_prep=prepare_data(True,16)
  train_loader,valid_loader,test_loader = data_prep.prepare()
  n_epochs=20
  train_on_gpu = torch.cuda.is_available()
  wandb.init()

  for epoch in range(1, n_epochs+1):
     

     train_loss = 0.0
     valid_loss = 0.0
     val_accuracy = 0.0
     train_acc=[]

     model.train()
     for data, target in train_loader:
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()     
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        pred=nn.functional.softmax(output,dim=1)
        accuracy = (torch.argmax(pred, dim=1) == target).float().mean()
        train_acc.append(accuracy)
        train_loss += loss.item()*data.size(0)
       
     model.eval()
     for data, target in valid_loader:
        optimizer.zero_grad()
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()
        output = model(data)
        loss = criterion(output, target)
        valid_loss += loss.item()*data.size(0)
        _, pred = torch.max(output, 1)    
        ps=nn.functional.softmax(output,dim=1)
        top_p,top_c= ps.topk(1,dim=1)
        equals= target == top_c.view(*target.shape)
        val_accuracy+= equals.type(torch.FloatTensor).mean()
    

     train_loss = train_loss/len(train_loader.dataset)
     valid_loss = valid_loss/len(valid_loader.dataset)
     val_accuracy = val_accuracy/len(valid_loader)
     
     log_dict = {"Train_loss": train_loss, "Validation_loss": valid_loss, "Validation_Accuracy": val_accuracy}
     print('Epoch: {} \tTraining Loss: {:.5f} \tValidation Loss: {:.5f} \tValidation Accuracy: {:.5f}'.format(epoch,
        train_loss, valid_loss,val_accuracy))    
     wandb.log(log_dict)
  return model

trained_model=train_resnet()