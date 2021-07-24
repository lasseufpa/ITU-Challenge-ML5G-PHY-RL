# Radio Strike main links
>Details about the challenge are available at http://ai5gchallenge.ufpa.br.

>Registration link: https://challenge.aiforgood.itu.int/match/matchitem/39

>Datasets and the renderer (CaviarRenderer-ITU-v1) are available at https://nextcloud.lasseufpa.org/s/WYZAMbSbdocs2DL

#  Data preprocessing

In this section, the dataset of episodes is filtered at each timerstamp, allowing only the desired users (e.g.: uav1, simulation_car1, simulation_pedestrian1) that will be used according to need, storing the parameters.

#### Script parameters:
```bash
python3 test_ep_reader.py Episode_ID Users_list
```

#### Usage example:

```bash
python3 ep_reader.py 0 uav1,simulation_car1,simulation_pedestrian1
```

