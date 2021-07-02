# Radio Strike

Details about the challenge and the datasets are available at http://ai5gchallenge.ufpa.br.

Registration link: https://challenge.aiforgood.itu.int/match/matchitem/39

Datasets are available at https://nextcloud.lasseufpa.org/s/WYZAMbSbdocs2DL

# Radio Strike Installation
This instructions will guide you through the process of using Radio Strike. 

## Setting up the environment to run the baseline codes
The provided RL agent uses [Stable-Baselines](https://github.com/Stable-Baselines-Team/stable-baselines) as its framework. Because of that, in our environment we need Python 3.6 and Tensorflow 1.14.

For the package management we adopted [Conda](https://docs.conda.io/en/latest/). To create a conda environment with Python 3.6 use the following command ([more info](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-python.html)):  

`$ conda create -n rstrike python=3.6 anaconda`

_OBS: Note that we named the environment as `rstrike`, but you can choose other name as you wish._

After its creation you need to activate the environment:

`$ conda activate rstrike`

and install these packages:

`$ pip3 install airsim tensorflow==1.14.0 stable-baselines==2.10.0`

With that you're ready to run the baseline.

``

## Data organization

The dataset is provided in `.csv` files, that are in the folder `episodes` (i.e `ep0.csv`, `ep1.csv` etc). Each `episode` is composed by the following columns:

|timestamp|obj|pos_x|pos_y|pos_z|orien_w|orien_x|
|---|---|---|---|---|---|---|

|orien_y|orien_z|linear_acc_x|linear_acc_y|linear_acc_z|linear_vel_x|linear_vel_y|
|---|---|---|---|---|---|---|

|linear_vel_z|angular_acc_x|angular_acc_y|angular_acc_z|angular_vel_x|angular_vel_y|angular_vel_z|
|---|---|---|---|---|---|---|

There are three different types of objects: `uav`, `simulation_car` and `simulation_pedestrian`. Only the `uav` type have information in all columns, while the others have only information regarding their position and orientation. 

## Baseline data
The baseline considers only the information from `uav1`, `simulation_car1` and `simulation_pedestrian1`. These three are the users (UEs) being served by the base station (BS).
