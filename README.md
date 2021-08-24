# Radio Strike main links
>Details about the challenge are available at http://ai5gchallenge.ufpa.br.

>Registration link: https://challenge.aiforgood.itu.int/match/matchitem/39

>Datasets and the renderer (CaviarRenderer-ITU-v1) are available at https://nextcloud.lasseufpa.org/s/WYZAMbSbdocs2DL

>Additional support material is available at https://nextcloud.lasseufpa.org/s/ZbB3cLN4MGZmwN4

# Part I) Radio Strike installation and usage
The instructions below will guide you through the process of installing and using the Radio Strike software, including its baseline RL agent and associated resources.

## I.1) Quick and dirty installation

1) First obtain the code and place it in a folder (we will assume here that the folder is called `radiostrike`). For instance, you can clone the repository and name the folder with:

       git clone https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git radiostrike

    Later, when issuing commands, remember to first go to the radiostrike folder with: 
    
       cd radiostrike
    
2) Now download the data in folder `episodes_dataset\training` from https://nextcloud.lasseufpa.org/s/WYZAMbSbdocs2DL .
This data is required by the Python code to generate the RL episodes. Make the corresponding CSV files (a total of 500 files) available at a folder called `radiostrike\episodes`.
For instance, you should have `radiostrike\episodes\ep0.csv`, `radiostrike\episodes\ep1.csv`, etc., assuming radiostrike is the folder in which you installed the repository.


3) Install required packages. The Python packages that we use in this tutorial (numpy, pandas, etc.) are listed in the file `requirements.txt`.

The baseline agent code provides an example of a simple reinforcement learning (RL) agent for the RadioStrike-noRT-v1 environment, as adopted for the PS-006 ITU Challenge.
The provided RL agent uses [Stable-Baselines](https://github.com/Stable-Baselines-Team/stable-baselines) as its framework. Because of that, in our environment we
need Python 3.6 and Tensorflow 1.14. Note that the participant is free to adopt a RL library other than Stable-Baselines and another deep learning framework (and eventually
use another Python version).

## I.2) Training and testing the baseline RL agent (when all dependencies are met)

If you are facing installation problems, please see the suggestions in other subsections below. In this subsection we assume you have successfully installed
all required packages. Hence, you can train the baseline RL agent with:

    python3 train_b-a2c.py -m <model_name> -ep <first_train_ep_id> <last_train_ep_id>

For example, to create an agent and save it in a file named `baseline.a2c`, training it on the data from episodes 0 to 399, the command is:

    python3 train_b-a2c.py -m baseline.a2c -ep 0 399

Recall that the provided data to create each episode must be available in folder `episodes`. After finishing the training, the agent will be stored in the `./model` folder, created automatically by the end of the first run.

To test the baseline RL agent you can run:

    python3 test_b-a2c.py -m <model_name> -ep <test_ep_id#1> <test_ep_id#n>

This will give you several output files in the folder `./data` named `actions_<model_name>_ep<ep_number>.csv`, in which there will be information regarding the actions performed by the agent
at each simulation step for all the episodes passed. For example, a file can have:

|chosen_ue|ue_index|beam_index|
|---|---|---|
simulation_pedestrian1|2|32
simulation_car1|1|63
uav1|0|	58

You can also get an output with more information by adding `--full-output` flag. This way the output file name is not `actions_<model_name>_ep<ep_number>.csv`, but `output_<model_name>_ep<ep_number>.csv` :

    $ python3 test_b-a2c.py -m <model_name> -ep <test_ep_id#1> <test_ep_id#n> --full-output
    
In this case, the output file will have several extra columns, as follows:    

|chosen_ue|ue_index|beam_index|x|y|z|pkts_dropped|
|---|---|---|---|---|---|---|
|simulation_pedestrian1|2|32|2.903349|33.66375|7.4372497|0.0

pkts_transmitted|pkts_buffered|bit_rate_gbps|channel_mag|reward|
|---|---|---|---|---|
157.0|805.0|0.6255017349493768|0.41372613018058246|0.2502006939797507|

For instance, to use a test set that is disjoint from the previous training set:

    python3 test_b-a2c.py -m baseline.a2c -ep 400 500

or

    python3 test_b-a2c.py -m baseline.a2c -ep 400 500 --full-output

## I.3) Training and testing the baseline dummy agents (when all dependencies are met)
Besides the RL agent, we also provide "dummy" agents for comparison purposes. There are two and they are called B-Dummy and B-BeamOracle. The B-Dummy agent assumes random action choices for both the scheduled user and which beam index to use. The B-BeamOracle agent follows a sequential user scheduling pattern (ue0-ue1-ue2-ue0-ue1-ue2...) and always uses the optimal beam index for the selected user.

Their operation is equal to the RL agent described above, and they are be called with:

    $ python3 test_b-dummy.py -ep <test_ep_id#1> <test_ep_id#n>
or

    $ python3 test_b-dummy.py -ep <test_ep_id#1> <test_ep_id#n> --full-output

for the B-Dummy, and

    $ python3 test_b-oracle.py -ep <test_ep_id#1> <test_ep_id#n>

or

    $ python3 test_b-oracle.py -ep <test_ep_id#1> <test_ep_id#n> --full-output

for the B-BeamOracle.

Their outputs are located in a specific folder inside `/data` named `./data/dummy` and `./data/beamoracle`, respectively, and are called `actions_b_dummy_<ep_number>` `output_b_dummy_<ep_number>` in case of the B-Dummy, or `actions_b_beam_oracle_<ep_number>` `output_b_beam_oracle_<ep_number>` in case of the B-BeamOracle.

## I.4) Plotting the results
To analyze the output data from the agent and the dummies, several tools for plotting charts are provided in the file `plot_tools.py`. You can use it as a class that can be called inside a script or in a quick and dirty way, in which you call it via terminal to plot all the charts available. 

Usage:

    $ python3 plot_tools.py -m <model_name> -ep <test_ep_id#first> <test_ep_id#last> --dummy --oracle

Example:

    $ python3 plot_tools.py -m baseline -ep 0 1 --dummy --oracle


To use it, some information must be provided: first the name of the tested RL model (only the name without extension), second, the episodes to test, and finally, if the user will plot the B-Dummy and the B-BeamOracle results as well. 

_Obs: To plot any results, they must be obtained first by running the baselines._ 

_Obs: The method `.read_data()` is used to read the output data of the baselines from an episode or interval of episodes. In case you use the class instead of the terminal version, remember to use `.read_data()` at the beginning of your script, before calling any plot method._

## I.5) Troubleshooting: typically due to broken dependencies

Most of the times one needs to fix dependencies and install specific versions of Python or its packages.

In this case, it is very convenient to use a virtual environment and better control the package versions.
Before proceeding with the installation below, please check if you already have Python installed with:

    python --version

_Obs: Be aware: if you already have Python installed, for instance on Windows, but not in a specific virtual environment, sometimes it is better to uninstall it and start from scratch to avoid conflicts._

_Obs: If you are using pip, it is useful to check with `pip freeze` the versions of the installed packages._

We will share below some suggestions to install a given Python version. Recall that because we are adopting the Stable-Baselines RL library, we have adopted Python 3.6.8. 

We will describe options for both Windows and Linux.

## I.6) On Windows: installing a virtual environment and a specific Python version 

You must first download the Python executable for the version you chose. We are assuming it is Python 3.6
and we will get it from the official [Python website](https://www.python.org/downloads/release/python-368/) (e.g. use this link to directly download for amd64: [Python3.6.exe](https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe))

_Obs: When starting the installation, check the box "Add Python 3.6 to PATH"_

Install Pip 

```python
python -m pip install --upgrade pip
```

Install Pipenv
```python
pip install --user pipenv
```

Because the provided Pipfile lists all dependencies, you can create the environment whith Python 3.6 and install all Radio Strike dependencies using:
```python
pipenv install --python 3.6
```

Activate your environment
```python
pipenv shell
```

You can check if you are using the correct python version with:

     python3 --version

and also the correct packages:

     pip3 freeze

With that you're ready to run the baseline.

## I.7) On Linux: installing a virtual environment with a specific Python version 

### Install pyenv
To manage python versions we use [pyenv](https://github.com/pyenv/pyenv). Note that there are many other alternatives to install Python versions. For instance, you can follow [link](https://tecadmin.net/install-python-3-6-ubuntu-linuxmint/).

 To install pyenv, first install the Python build dependencies:
 
    $ sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \ libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \ libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

then, install `pyenv` with:

    $ curl https://pyenv.run | bash

and add the following in `~/.bashrc` if you use bash, or `~/.zshrc` with you use zsh, to enable `pyenv` in the terminal: 

    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"

Restart your shell so the path changes take effect:

    $ exec $SHELL
    
### Download the Python version you want

In our case (to run our Stable Baselines), we download Python 3.6.8:

    $ pyenv install 3.6.8


### Install pipenv 

For setting up the environment and performing package management, we assume here [pipenv](https://pipenv.pypa.io/en/latest/). 

#### Ubuntu

    $ pipx install pipenv

For other distributions refer to [pipenv installation guide](https://pypi.org/project/pipenv/#description).

#### Required packages

Because the provided Pipfile lists all dependencies, you can create the environment whith Python 3.6 and install all Radio Strike dependencies using:
```python
pipenv install --python 3.6
```

Activate your environment
```python
pipenv shell
```

You can check if you are using the correct python version with:

     python3 --version

and also the correct packages:

     pip3 freeze

With that you're ready to run the baseline.



## I.8) Radio Strike Renderer

Download the renderer CaviarRenderer-ITU-v1 from https://nextcloud.lasseufpa.org/s/WYZAMbSbdocs2DL .

AirSim needs to find a specific configuration file that we created for Radio Strike. Hence, you should download the [AirSim settings file](https://nextcloud.lasseufpa.org/s/WYZAMbSbdocs2DL?path=%2FCaviarRenderer-ITU-v1%2FAirSim) called settings.json and put
this file in a folder called `Airsim`, within the folder `Documents`. According to the [AirSim 
documentation](https://github.com/microsoft/AirSim/blob/master/docs/settings.md), this 
AirSim subfolder is located at Documents\AirSim on Windows and ~/Documents/AirSim on Linux systems.

At this point the CaviarRender can be executed, to visualize the results in the 3D scenario the *Render mode* needs to be enabled in the configuration menu of CaviarRender.

In order to have a faster execution, it is possible to disable the Unreal Engine graphics by changing the AirSim settings ViewMode.
To do that, change **"ViewMode": ""** to **"ViewMode": "NoDisplay"** in the file `settings.json` mentioned above.

CaviarRenderer-ITU-v1 performs two distinct things:

1) After having trained a RL agent, CaviarRenderer-ITU-v1 is used to 
visualize the RL agent actions in the 3D scenario. It indicates the beam directions and also
the scheduled user (by drawing a bounding box around it). To execute it:

With the 3D scenario running it is possible to visualize the results using the *caviar_render.py* script. This script runs one episode per
execution and it is necessary to set the episode path in the begin of the script and also the output files with the RL results.

    python3 caviar_render.py

The output of this script is a video with the simulation result. It is currently not feasible to visualize the 3D scenario along the RL training stage. But this is in our "to do" list.

2) CaviarRenderer-ITU-v1 can also be used to create additional episode data, storing the information as .CSV files.
You can of course use it to create more episodes for your research, 
but you *cannot* use any extra episodes when training your model for the PS-006 ITU Challenge. The rules restrict
the models to be trained only with the provided episodes.

The first step to generate new episodes is to create a set of trajectories to be used by the AirSim's UAVs.

The trajectories available [here](https://nextcloud.lasseufpa.org/s/WYZAMbSbdocs2DL?path=%2FCaviarRenderer-ITU-v1%2Fway_points) can be used,
or new trajectories can be generated using the **random_generator.py** script. It is possible to define the number of trajectories to  be generated by the script.

	cd waypoints/
	python3 random_generator.py
	
With the trajectories ready, the CaviarRender should be executed and, in its menu, choose to disable its **Render mode**.
Now it is possible to run the **ep_generator.py** script.

	python3 random_generator.py
	
The number of episodes, sample rate, trajectories paths and others configurations can be changed in the being of the **ep_generator.py** script.

# Part II) Data organization

The dataset is provided in `.csv` files, that are in the folder `episodes` (i.e `ep0.csv`, `ep1.csv` etc). Each `episode` has approximately 3 minutes of duration, with information stored with a sampling interval of 10 ms. The csv is composed by the following columns:

|timestamp|obj|pos_x|pos_y|pos_z|orien_w|orien_x|
|---|---|---|---|---|---|---|

|orien_y|orien_z|linear_acc_x|linear_acc_y|linear_acc_z|linear_vel_x|linear_vel_y|
|---|---|---|---|---|---|---|

|linear_vel_z|angular_acc_x|angular_acc_y|angular_acc_z|angular_vel_x|angular_vel_y|angular_vel_z|
|---|---|---|---|---|---|---|

There are three different types of objects: `uav`, `simulation_car` and `simulation_pedestrian`. Only the `uav` type has information in all columns, while the others have only information regarding their position and orientation. 
## Airsim coordinates
Airsim uses a coordinate type other than unreal, called NED coordinates system, i.e., +X is North, +Y is East and +Z is Down, and the units are in S.I. different from the Unreal Engine which uses centimeters. For more information see [Airsim Documentation](https://github.com/microsoft/AirSim/blob/master/docs/apis.md).
## Baseline data
An episode has information regarding all mobile objects in a scene (all pedestrians, etc.). To keep it simple, we assumed that the baseline RL agent uses only information from the three users (`uav1`, `simulation_car1` and `simulation_pedestrian1`). These are the user equipment (UEs) being served by the base station (BS). Hence, the baseline data was obtained by filtering the original episodes to discard the information about all other mobile objects (which are scatterers, not UEs).

# Part III) Evaluation

## III.1) What the participant must deliver

The participant must provide: 
- The predicted output for the test set as a CSV (comma-separated values) file.

  _Obs1: This output can be generated with `test_b-a2c.py`, you just need to pass your model in the argument (the name "b-a2c" comes from the baseline, but you're free to use other RL strategies)._

  _Obs2: This output must contain *at least* the actions of the agent, namely the scheduled user ID and the chosen beam index, for each time step from the test set._

- The participant must also provide two video files:

  - one with the rendering of the RL agent for the episode with the largest value for the return `G`; 
  - and another for the episode with the smallest value of `G`.
   
  _Obs1: These two videos should correspond to the output of CaviarRenderer-ITU-v1 (or later version). If desired, the participant can concatenate the two into a single video._
  
  _Obs2: Another option is to expand the video (or videos) by promoting the designed RL agent, describing its architecture or any other thing the participant thinks is interesting. This promoting video must be recorded in Portuguese or English (the organizers can generate the videos for the participants if needed)._

## III.2) Evaluation metric
The participant with the best return `G` over the test episodes wins. In case of a draw regarding the average return `G` among distinct participants, the tie will be broken using the best video(s).

Note that for the evaluation, the return `G` 

<img src="https://render.githubusercontent.com/render/math?math=\large \color{red} G = \sum_{}^{}r[t]">,

is going to be calculated with the same reward <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} r[t]"> as the baseline agent (`B-A2C`)

<img src="https://render.githubusercontent.com/render/math?math=\large \color{red} r[t] = \frac{P_{\textrm{tx}}[t]-2 P_{d}[t]}{P_{b}[t]}">,

where <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} P_{\textrm{tx}}[t]">, <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} P_{d}[t]">, and <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} P_{b}[t]"> correspond, respectively, to the total amount (summation for all users) of transmitted, dropped and buffered packets at time <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} t">. 

  _Obs1: The reward <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} r[t]"> is restricted to the range <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} -2 \le r[t] \le 1">. At each time <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} t">, a single user can be served, but <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} P_{b}[t]"> accounts for the number of packets in all three buffers. Hence, <img src="https://render.githubusercontent.com/render/math?math=\large \color{red} r[t] = 1"> only if all buffered packages of the scheduled user are transmitted,  while the buffers of the other two users were empty._

  _Obs2: The participant is free to use other rewards, states and RL methods (DQN, A3C, etc.) in the agent design and training._
