# Radio Strike

Here you find the code for the “ITU-ML5G-PS-006: ML5G-PHY-Reinforcement learning: scheduling and resource allocation”, which is part of the “ITU Artificial Intelligence/Machine Learning in 5G Challenge. 

Details about this challenge are available at http://ai5gchallenge.ufpa.br.

Registration link: https://challenge.aiforgood.itu.int/match/matchitem/39

Datasets are available at https://nextcloud.lasseufpa.org/s/WYZAMbSbdocs2DL

# Radio Strike Installation
The instructions will guide you through the process of using Radio Strike and associated resources. 

## Setting up the environment to run the baseline codes
The baseline provides an example of a simple reinforcement learning (RL) agent for the RadioStrike-noRT-v1 environment, as adopted for the PS-006 ITU Challenge.
The provided RL agent uses [Stable-Baselines](https://github.com/Stable-Baselines-Team/stable-baselines) as its framework. Because of that, in our environment we need Python 3.6 and Tensorflow 1.14. Note that the participant is free to adopt a RL library other than Stable-Baselines and deep learning framework.

For setting up the environment and performing package management, we assume here [Conda](https://docs.conda.io/en/latest/). Again, the participant can use other tools. To create a conda environment with Python 3.6 use the following command ([more info](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-python.html)):  

`$ conda create -n rstrike python=3.6 anaconda`

_OBS: Note that we named the environment as `rstrike`, but you can choose other name as you wish._

After its creation you need to activate the environment:

`$ conda activate rstrike`

and install these packages:

`$ pip3 install airsim tensorflow==1.14.0 stable-baselines==2.10.0`

With that you're ready to run the baseline.

``

## Training and testing the baseline RL agent
To train you must run:

`$ python3 train_agent.py 'agent_name' 'number_of_train_episode'`

For example, to create an agent named `test.a2c`, trained on the data from episode 0, the command is:

`$ python3 train_agent.py test 0`

After finishing the training, the agent will be stored in a `./model` folder, created automatically by the end of the first run.

To test your agent you must run:

`$ python3 test_agent.py 'agent_name' 'number_of_test_episode'`

Similarly, to test the agent from the example above in the same episode, one should run:

`$ python3 test_agent.py test 0`

This will create a folder named `./data` in which the actions of the agent will be stored. The actions will receive the name `actions_'agent_name'.csv`.
