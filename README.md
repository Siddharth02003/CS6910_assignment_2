# CS6910_assignment_2
1. Clone this repository
   ```bash
   git clone https://github.com/Siddharth02003/CS6910_assignment_2.git
   ```
2. Install the required packages
   ```bash
   pip3 install -r requirements.txt
   ```
Peek inside the requirements file if you have everything already installed. Most of the dependencies are common libraries.

Running the model 

```sh
python cs6910_assignment_2a.py --sweep <> --num_dense_dims <> --batch_norm <> --activation<> --num_filters <> --kernel_size <> --dropout <> --augment <> --n_epochs <> --batch_size <> --learning_rate <> 
```
Enter the parameter you would like to change in the place of <>. The default values of each parameter are mentioned below.
<br>

**Description of various command line arguments**<br>
1. `--sweep` : Yes or No <br>
2. `--batch_norm` : Batch Normalization: True or False (Default: False)  <br>
3. `--num_filters` : Number of Filters: List with each integer element telling number of filters per conv layer (Default: [128,128,64,64,32]) <br>
4. `--kernel_size` : Kernel Size: List with each integer element telling kernel_size per conv layer (Default: [3,3,3,3,3]) <br>
5. `--dropout` : Dropout: float value (Default:0.2)
6. `--augment` : Data Augmentation: True or False (Default: True)
7. `--n_epochs` : Number of Epochs: integer value (Default: 10)
8. `--batch_size` : Batch Size: integer value (Default: 32)
9. `--num_dense_dim` : Number of neurons in Dense Layer: integer value (Default: 256)
10. `--learning_rate` : Learning Rate: float value (Default: 0.001)
