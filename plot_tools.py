'''
UFPA - LASSE - Telecommunications, Automation and Electronics Research and Development Center - www.lasse.ufpa.br
CAVIAR - Communication Networks and Artificial Intelligence Immersed in Virtual or Augmented Reality
Ailton Oliveira, Felipe Bastos, João Borges, Emerson Oliveira, Daniel Suzuki, Lucas Matni, Rebecca Aben-Athar, Aldebaro Klautau (UFPA): aldebaro@ufpa.br
CAVIAR: https://github.com/lasseufpa/ITU-Challenge-ML5G-PHY-RL.git


Auxiliary methods for plotting
V1.0
'''
import argparse
from typing import List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

class PlotTools():
    def __init__(self,  model_name, dummy=True, oracle=True):
        # Defines eps as a list
        self.model_name = model_name
        self.dummy = dummy
        self.oracle = oracle
        self.metrics = {
            'chosen_ue':'User',
            'ue_index':'ue_index',
            'beam_index': 'Beam Index',
            'pkts_dropped': 'Dropped packets',
            'pkts_transmitted': 'Transmitted packets',
            'pkts_buffered': 'Buffered packets',
            'bit_rate_gbps': 'Bit Rate (Gbps)',
            'channel_mag': 'Channel Magnitude',
            'reward': 'Reward'
        }

    def read_data(self, eps):
        """
        Read baseline data within an episode  or an episode interval
        """
        if len(eps) >= 2:
            self.eps = range(eps[0], eps[1] + 1)
        else:
            self.eps = eps
        # Read the data
        dfs = []
        titles = []

        if self.dummy:
            df_dummy = []
            ep = []
            for ep in self.eps:
                df = pd.read_csv('./data/dummy/'+'output_dummy_ep'+ str(ep)+'.csv')
                self._rename(df)
                df['ep'] = ep
                df_dummy.append(df)

            df_dummy = pd.concat(df_dummy, axis=0)
            df_dummy['title'] = 'B-Dummy'
            dfs.append(df_dummy)
            titles.append('B-Dummy')
        
        if self.oracle:
            df_oracle = []
            for ep in self.eps:
                df = pd.read_csv('./data/beamoracle/'+'output_b_beam_oracle_ep'+ str(ep)+ '.csv')
                self._rename(df)
                df['ep'] = ep
                df_oracle.append(df)

            df_oracle = pd.concat(df_oracle, axis=0)
            df_oracle['title'] = 'B-BeamOracle'
            dfs.append(df_oracle)
            titles.append('B-BeamOracle')

        df_rl = []
        for ep in self.eps:
            df = pd.read_csv('./data/'+'output_' + self.model_name +'_ep'+str(ep)+'.csv')
            self._rename(df)
            df['ep'] = ep
            df_rl.append(df)

        df_rl = pd.concat(df_rl, axis=0)
        df_rl['title'] = 'B-A2C'
        dfs.append(df_rl)
        titles.append('B-A2C')

        self.titles = titles
        self.df_list = dfs

    def plot_density(self, feature, subplot=False, definition=.05, size=4):
        """
        Plot the density (KDE) graphic of given feature
        """
        if subplot:
            self._density(df=self.df_list, feature=feature,definition=definition, size=size)
        else:
            for df in self.df_list:
                self._density(df=[df], feature=feature,definition=definition, size=size)
        plt.show()

    def plot_hist(self, feature, size=3, definition=.05):
        """
        Plot a histogram of a feature
        """
        for title, df in zip(self.titles, self.df_list):
            binwidth = max(df[feature])*definition
            sns.histplot(df, x=feature, hue='Legend', binwidth=binwidth, element='step', legend=True)
            plt.title(title)
            plt.show()
        
    def plot_time(self, feature, ep=False):
        """
        Plot a feature over time, if given an episode 'ep', then the plot is over the timesteps of episode 'ep'
        """
        # If an episode is given, the dataframe list is restricted to that given episode
        if ep:
            df_list = []
            for df in self.df_list:
                df_list.append(self._episode(df, ep))
        else:
            df_list = self.df_list
        rows = len(self.titles)
        # Gerenate a subplot with 3 rows (or less) for each baseline/rl agent
        self._plot(rows = rows, df_list = df_list, feature = feature, ylabels = feature, xlabel = 'Time Steps', titles = self.titles)
        plt.show()

    def plot_time_ep(self, feature):
        """
        Plot a the total sum of a feature over the episodes
        """
        for df, title in zip(self.df_list, self.titles):
            value_per_ep = []
            for ep in self.eps:
                data = df.loc[df.ep == ep]
                value_per_ep.append(np.sum(data[feature]))

            plt.plot(self.eps, value_per_ep)
            plt.title(title + '-' + feature + ' per Episode')
            plt.ylabel(feature)
            plt.xlabel('Episodes')
            plt.show()

    def plot_hist_ep(self, feature, definition=.1):
        """
        Plot histogram of the occurences of total sum of a feature in all episodes
        """
        mpl.style.use('seaborn-dark')
        rows = len(self.titles)
        fig = plt.figure(figsize=[6,6])
        lim_x = []
        # Gather the total sum of 'feature' for each episode
        for df, title, row in zip(self.df_list, self.titles, range(rows)):
            value_per_ep = []
            for ep in self.eps:
                # Select the related to the episode ep from the dataframe df
                data = self._episode(df, ep)
                value_per_ep.append(np.sum(data[feature]))
            lim_x.append(value_per_ep)
            # Define the bins according to the definition
            bins = int(1/definition)
            plt.hist(value_per_ep, bins=bins, alpha=0.5, label=title)
        
        plt.title('Total '+ feature + ' per Episode')
        plt.legend()
        plt.xlabel(feature)
        plt.xlim(np.min(lim_x)-30, np.max(lim_x))
        plt.ylabel('Occurrence in Episodes')
        plt.grid()
        plt.show()
    
    def plot_metrics(self):
        """
        Plot general metrics over time steps (Reward, Transmitted packets, Dropped packets, Buffered packets)
        """
        metrics = ['Reward', 'Transmitted packets', 'Dropped packets', 'Buffered packets']
        for df, baseline in zip(self.df_list, self.titles):
            df = self._episode(df, self.eps[0])
            fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(8, 8))
            ax[0].set_title(baseline + ' Episode ' + str(self.eps[0]))
            for i, feature in zip(range(4),metrics):
                ax[i].plot(df[feature])

            # Set label y for every plot
            for a, feature in zip(ax.flat, metrics):
                a.set(ylabel=feature)

            # Hide x labels and tick labels for top plots and y ticks for right plots.
            for a in ax.flat:
                a.label_outer()
            plt.xlabel('Time Steps')
            plt.show()
        
    def plot_cumulative(self, feature, size=4):
        """
        Plot the cumulative sum of an feature over the time steps
        """
        for df in self.df_list:
            feature_sum = 0
            cache = []
            for data in df[feature]:
                feature_sum += data
                cache.append(feature_sum)
            plt.plot(range(len(cache)), cache)
        plt.legend(self.titles)
        plt.ylabel('Cumulative '+feature)
        plt.xlabel('Time steps')
        plt.show()
            

    def plot_all(self):
        """
        Plot general metrics at once (Recommended)
        """
        self.plot_cumulative( feature='Reward')
        self.plot_metrics()
        self.plot_density(feature='Reward')
        self.plot_density(feature='Transmitted packets')
        self.plot_density(feature='Dropped packets')
        self.plot_density(feature='Buffered packets')
        self.plot_hist_ep(feature='Reward')

    def _rename(self, df):
        # Change users names
        legend={
        'uav1': 'UAV',
        'simulation_car1': "Car",
        'simulation_pedestrian1': 'Pedestrian'
        }
        df['Legend'] = df.chosen_ue.map(legend)
        return df.rename(columns=self.metrics, inplace=True)
    
    def _plot(self, rows, df_list, feature, ylabels, xlabel, titles = [''], figsize = [6,8]):
        fig, ax = plt.subplots(nrows=rows, ncols=1, figsize=figsize)
        for title, df, row in zip(titles, df_list, range(rows)):
            ax[row].plot(df[feature])
            ax[row].set_title(title)
        # Set label for y for every plot
        for a in ax.flat:
            a.set(ylabel=ylabels)

        # Hide x labels and tick labels for top plots and y ticks for right plots.
        for a in ax.flat:
            a.label_outer()

        plt.xlabel(xlabel)
    
    def _episode(self, dataframe, ep):
        return dataframe.loc[dataframe.ep == ep]
    
    def _density(self, df, feature, definition=0.05, size=3):
        dfs = pd.concat(df, axis=0)
        g = sns.displot(dfs, x=feature, hue='Legend', row='title', kind="kde", bw_adjust=definition, fill=True, legend=True, aspect=2, height=size)
        g.set_titles("{row_name}")

'''
The file provides a class with several plot utilities. 
However, the user can also call from the terminal to perform
a quick plot. 

Usage:

$ python3 plot_tools.py -m <model_name> -ep <test_ep_id#first> <test_ep_id#last> --dummy --oracle

Example:

$ python3 plot_tools.py -m baseline -ep 0 1 --dummy --oracle
'''

parser = argparse.ArgumentParser()

parser.add_argument("--model", "-m", 
                    help="Pass RL model name",
                    action="store", 
                    dest="model", 
                    type=str)

parser.add_argument("--episode", "-ep",
                    nargs='+',
                    help="IDs of the first and " +
                         "last episodes to test",
                    action="store", 
                    dest="episode", 
                    type=int)

parser.add_argument("--dummy", "-d",
                    help="If activated, plots dummy output as well",
                    action="store_true", 
                    dest="dummy")

parser.add_argument("--oracle", "-o",
                    help="If activated, plots oracle output as well",
                    action="store_true", 
                    dest="oracle")
                   
args = parser.parse_args()

plotter = PlotTools(model_name=args.model, dummy=args.dummy, oracle=args.oracle)

plotter.read_data(eps=args.episode)
plotter.plot_all()