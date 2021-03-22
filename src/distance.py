from typing import Tuple

import numpy as np


class Distance:
    """"Distance class is employed to calculate a distance between two points.

    This class provides a handy set of methods to be used whenever a distance
    needs to be calculated.

    """

    @staticmethod
    def euclidean_distance(point1: Tuple[float, float], point2: Tuple[float, float]):
        """Calculate the Euclidean distance of two points.

        Args:
            point1 (Tuple[float, float]): The first point.
            point2 (Tuple[float, float]): The second point.

        Returns:
            float: The distance.
        """

        x1, y1 = point1
        x2, y2 = point2
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @staticmethod
    def manhattan_distance(point1: Tuple[float, float], point2: Tuple[float, float]):
        """Calculate the Manhattan distance of two points.

        Args:
            point1 (Tuple[float, float]): The first point.
            point2 (Tuple[float, float]): The second point.

        Returns:
            float: The distance.
        """

        x1, y1 = point1
        x2, y2 = point2
        return np.abs(x2 - x1) + np.abs(y2 - y1)

    @staticmethod
    def map_str_to_function(function_name: str):
        """Map the function name into the function reference.

        Args:
            function_name (str): The name of the distance function.

        Returns:
            function: The distance function object.
        """

        if function_name == Distance.euclidean_distance.__name__:
            return Distance.euclidean_distance
        elif function_name == Distance.manhattan_distance.__name__:
            return Distance.manhattan_distance
