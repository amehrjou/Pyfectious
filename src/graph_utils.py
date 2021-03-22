import itertools
from typing import List, Tuple

from igraph import Graph, plot


def same_family(first_person, second_person) -> bool:
    """Check whether two person have the same family or not.

    Args:
        first_person (Person): The first input person.
        second_person (Person: The second input person.

    Returns:
        bool: True, if the families match. Otherwise, returns False.
    """
    if first_person.family is second_person.family:
        return True
    return False


def same_person(first_person, second_person) -> bool:
    """Check whether two person are the same or not.

    Args:
        first_person (Person: The first input person.
        second_person (Person: The second input person.

    Returns:
        bool: True, if the persons match. Otherwise, returns False.
    """
    if first_person is second_person:
        return True
    return False


def build_family_graphs(people: List) -> Graph:
    """Create the graph of families.

    This method builds the graph in which each person is represented
    by a node in the graph, and an edge exists between two person if
    they are in the same family.

    Args:
        people List[Person]: The population for which the graph is built.

    Returns:
        Graph: The population family graph object.
    """
    family_graph_edges = list()

    # construct the list of edges
    for from_person in people:
        for to_person in people:
            if same_family(from_person, to_person) and not same_person(from_person, to_person):
                family_graph_edges.append((from_person.id_number, to_person.id_number))

    population_family_graph = Graph()
    population_family_graph.add_vertices(len(people))
    population_family_graph.vs["name"] = \
        [str(person.id_number) for person in people]
    population_family_graph.vs["label"] = population_family_graph.vs["name"]
    population_family_graph.add_edges(family_graph_edges)

    return population_family_graph


def plot_graph(graph: Graph, layout: str = "fr", size: Tuple = (800, 800), margin: int = 20,
               save: bool = False, file: str = "graph.png"):
    """Plot the graph of a given graph object.

    Args:
        graph (Graph): The graph object.

        layout (str, optional): The layout of the graph according to igraph docs.
        Defaults to "fr".

        size (Tuple[int, int], optional): Size of the plot. Defaults to (800, 800).

        margin (int, optional): The margin of graph with respect to the picture.
        Defaults to 20.

        save (bool, optional): Save the graph plot in the file address. Defaults to False.
        file (str, optional): The file name or address given to save the plot.
        Defaults to "graph.png".

    """
    visual_style = dict()
    visual_style["layout"] = graph.layout(layout)
    visual_style["bbox"] = size
    visual_style["margin"] = margin
    out = plot(graph, **visual_style)

    if save:
        out.save(file)

    return out


def has_connection(first_person, second_person, graph) -> bool:
    """Check the connection based on the background graph in simulation.

    Args:
        first_person: The first input person.
        second_person: The second input person.
        graph: The background graph of simulation, simulator.graph.

    Returns:
        bool: True, if a connection exists, False otherwise.
    """
    for person_id in graph[first_person.id_number]:
        if second_person.id_number == person_id:
            return True
    return False


def build_community_graph(simulator) -> Graph:
    """Build the population graph based on the people in the same community.

    Args:
        simulator (Simulator): The simulator environment, containing the graph,
        communities, and people.


    Returns:
        Graph: The population community graph.
    """
    community_graph_edges = list()

    for community_id in simulator.communities:
        for community in simulator.communities[community_id]:
            community_people = list()

            for key in community.people_ids_dict:
                community_people += community.people_ids_dict[key]

            for element in itertools.product(community_people, community_people):
                first_person = simulator.people[element[0]]
                second_person = simulator.people[element[1]]
                if not same_person(first_person, second_person) and has_connection(first_person, second_person,
                                                                                   simulator.graph):
                    community_graph_edges.append(element)

    population_community_graph = Graph()
    population_community_graph.add_vertices(len(simulator.people))
    population_community_graph.vs["name"] = \
        [str(person.id_number) for person in simulator.people]
    population_community_graph.vs["label"] = population_community_graph.vs["name"]
    population_community_graph.add_edges(community_graph_edges)

    return population_community_graph
