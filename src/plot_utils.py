from collections import Counter
from datetime import datetime
from typing import List

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
import seaborn as sns


class Plot:
    """A class to provide handy plots whenever required before, during, and after
    the simulation.

    """

    @staticmethod
    def plot_hist(x_data: List, x_label: str, density: bool = False, fit_curve: bool = False, title: str = None):
        """Plot a histogram.

        Args:
            x_data (List): Items to be plotted.
            x_label (str): Label of the X axis.

            density (bool, optional): If True, the first element of the return
            tuple will be the counts normalized to form a probability density,
            i.e., the area (or integral) under the histogram will sum to 1. Defaults to False.

            fit_curve (bool, optional): Decide whether to fit a curve to the plot.
            Defaults to False.

            title (str, optional): Title of the plot. Defaults to None.
        """
        plt.figure(figsize=(12, 12))
        plt.hist(x_data, density=density, bins=30, label=x_label)
        if density and fit_curve:
            mini, maxi = plt.xlim()
            plt.xlim(mini, maxi)
            kde_xs = np.linspace(mini, maxi, 301)
            kde = scipy.stats.gaussian_kde(x_data)
            plt.plot(kde_xs, kde.pdf(kde_xs), label="PDF")
            plt.ylabel('Probability')
            plt.legend(loc="upper left")
        else:
            plt.ylabel('Frequency')
        plt.xlabel(x_label)
        if title:
            plt.title(title)
        plt.show()

    @staticmethod
    def plot_barplot(x_data: List, x_label: str, labels: List[str] = None, title: str = None):
        """Plot a bar plot.

        Args:
            x_data (List): The data to be plotted.
            x_label (str): Label of the data.
            labels (List[str], optional): The list of labels if required. Defaults to None.
            title (str, optional): Title of the plot. Defaults to None.
        """
        plt.figure(figsize=(12, 12))
        x_data = Counter(x_data)
        if len(labels) == 0:
            labels = x_data.keys()

        x_pos = [i for i, _ in enumerate(labels)]
        energy = x_data.values()

        plt.style.use('ggplot')
        plt.bar(x_pos, energy, color='green')
        plt.xlabel(x_label)
        plt.ylabel("Frequency")
        if title:
            plt.title(title)

        plt.xticks(x_pos, labels)

        plt.show()

    @staticmethod
    def plot_multiple_lines(x_data: List, y_data: List[List], x_label: str = "X", y_label: str = "Y", title: str = ""):
        """Plot a multiple line figure.

        Args:
            x_data (List): The X axis data.
            y_data (List[List]): The Y axis data containing multiple lists.
            x_label (str, optional): Label of the X axis. Defaults to "X".
            y_label (str, optional): Label of the Y axis. Defaults to "Y".
            title (str, optional): Title of the plot. Defaults to None.
        """
        plt.figure(figsize=(12, 12))
        sns.set_theme(context='paper', style="darkgrid",
                      font_scale=1.75, rc={'figure.figsize': (12, 12)})

        for data in y_data:
            ax = sns.lineplot(x=x_data, y=data, linewidth=3)

        # Must be removed if the simulation time is longer than a year
        if isinstance(x_data[0], datetime):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

        ax.axes.set_title(title, fontsize=25)
        ax.set_xlabel(x_label, fontsize=20)
        ax.set_ylabel(y_label, fontsize=20)

        plt.show()
        return plt

    @staticmethod
    def plot_line(x_data: List, y_data: List, x_label: str = "X", y_label: str = "Y", title: str = ""):
        """Plot a simple line figure.

        Args:
            x_data (List): The X axis data.
            y_data (List): The Y axis data.
            x_label (str, optional): Label of the X axis. Defaults to "X".
            y_label (str, optional): Label of the Y axis. Defaults to "Y".
            title (str, optional): Title of the plot. Defaults to None.
        """
        Plot.plot_multiple_lines(x_data, [y_data], x_label, y_label, title)

    @staticmethod
    def plot_map(Xs: List, Ys: List, colors: List, x_label: str = "X", y_label: str = "Y", title: str = None):
        """Plot a simple map of a given list, e.g., people.

        Args:
            Xs (List): The X axis data.
            Ys (List): The Y axis data.
            colors (List): Colors of the plot.
            x_label (str, optional): Label of the X axis. Defaults to "X".
            y_label (str, optional): Label of the Y axis. Defaults to "Y".
            title (str, optional): Title of the plot. Defaults to None.
        """
        plt.figure(figsize=(12, 12))
        plt.scatter(Xs, Ys, c=colors)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if title:
            plt.title(title)
        plt.show()

    @staticmethod
    def plot_map_with_communities(Xs: List, Ys: List, colors: List, communities_x: List, communities_y: List
                                  , community_sizes: List, x_label: str = "X", y_label: str = "Y", title: str = None):
        """Plot a single map with communities involved.

        Args:
            Xs (List): The X axis data.
            Ys (List): The Y axis data.
            colors (List): Colors of the plot.
            communities_x (List): Communities of the X axis data.
            communities_y (List): Communities in the Y axis data.
            community_sizes (List): A list containing the size of each community.
            x_label (str, optional): Label of the X axis. Defaults to "X".
            y_label (str, optional): Label of the Y axis. Defaults to "Y".
            title (str, optional): Title of the plot. Defaults to None.
        """
        plt.figure(figsize=(12, 12))
        plt.scatter(Xs, Ys, c=colors)
        plt.scatter(communities_x, communities_y, c='b', alpha=0.3, s=community_sizes)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if title:
            plt.title(title)
        plt.show()

    @staticmethod
    def plot_dot(x_data: List, y_data: List, x_label: str = "X", y_label: str = "Y", title: str = "",
                 marker_size: int = 100):
        """Plot a simple dot figure.

        Args:
            x_data (List): The X axis data.
            y_data (List): The Y axis data.
            x_label (str, optional): Label of the X axis. Defaults to "X".
            y_label (str, optional): Label of the Y axis. Defaults to "Y".
            title (str, optional): Title of the plot. Defaults to None.
            marker_size (int, optional): The size of the markers in plot. Defaults to 100.
        """
        sns.set_theme(context='paper', style="darkgrid", font_scale=1.75, rc={'figure.figsize': (12, 12)})
        ax = sns.scatterplot(x=x_data, y=y_data, palette="deep", s=marker_size)

        # Must be removed if the simulation time is longer than a year
        if isinstance(x_data[0], datetime):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

        ax.axes.set_title(title, fontsize=25)
        ax.set_xlabel(x_label, fontsize=20)
        ax.set_ylabel(y_label, fontsize=20)


if __name__ == '__main__':
    # Generate basic example here
    pass
