"""Classes that represent different types of questions supported by Graph Quest.

To create a new question type, extend one of the base classes and implement its methods.
"""
from abc import ABC, abstractmethod
import networkx as nx


class Question(ABC):
    """Abstract base class for all question types.

    Do not directly extend this class. Instead, extend its children (e.g. QTextInput).
    """
    def __init__(self,
                 layout='force-directed',
                 feedback=False,
                 node_prefix='',
                 label_style='none',
                 data=None,
                 highlighted_nodes=None,
                 highlighted_edges=None):
        self.layout = layout
        self.feedback = feedback
        self.node_prefix = node_prefix
        self.label_style = label_style
        self.data = data
        self.highlighted_nodes = highlighted_nodes
        self.highlighted_edges = highlighted_edges

    @abstractmethod
    def generate_data(self) -> list[nx.Graph]:
        """Generates a list of NetworkX graphs for the question.

        Returns
        -------
        graphs : [networkx Graph]
            A list of NetworkX Graphs.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def generate_question(self, graphs: list[nx.Graph]) -> str:
        """Generates the wording of the question.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        Returns
        -------
        description : str
            The question description.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def generate_solutions(self, graphs: list[nx.Graph]) -> list[any]:
        """Generates a set of possible solutions.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        Returns
        -------
        solutions : [any]
            A set of possible solutions.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def generate_feedback(self, graphs: list[nx.Graph], answer: any) -> (bool, str):
        """Generates a message to be displayed when the solution has been submitted.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        answer : any
            The student's choice of answer.

        Returns
        -------
        (result, explanation) : (bool, str)
            A pair: whether the answer is correct, and the message to be displayed.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError


class QSelectPath(Question):
    """Select a path in a given graph.

    The student will select the path by tapping on nodes in the graph.
    The answer is represented as a list of integers, e.g. `[0, 3, 5, 2]`.

    The question will only allow the student to select a valid simple path in the graph.

    Attributes
    ----------
    layout : str
        `"force-directed"` [default] | `"circle"` | `"grid"` | `"bipartite"`
        Determines the layout style for the graph.

    feedback : bool
        If `True`, use the `generate_feedback()` method,
        otherwise use the `generate_solutions()` method for verifying answers.

    node_prefix : str
        A prefix to prepend onto vertex labels.

    label_style : str
        `"none"` [default] | `"math"`
        Determines the style for node labels.

    data : None | any
        Persistent storage. You can set `data` to anything that is JSON serializable,
        and it will still be accessible if/when the `generate_feedback()` method is called.

    highlighted_nodes : None | list[int]
        A list of nodes to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    highlighted_edges : None | list[list[int, int]]
        A list of edges to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.
    """
    def __init__(self, layout='force-directed', feedback=False, node_prefix='', label_style='none', data=None,
                 highlighted_nodes=None, highlighted_edges=None):
        super().__init__(layout=layout, feedback=feedback, node_prefix=node_prefix, label_style=label_style, data=data,
                         highlighted_nodes=highlighted_nodes, highlighted_edges=highlighted_edges)

    @abstractmethod
    def generate_solutions(self, graphs: list[nx.Graph]) -> list[list[int]]:
        """Generates a list of possible solutions.

        Each solution is itself a list of vertices.
        For example, the return value could be

        [[0, 3, 5, 2],
         [0, 3, 4, 2]]

        Indicating there are 2 possible solutions: the path `[0, 3, 5, 2]` and the path `[0, 3, 4, 2]`.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question. They will be
            labelled in-order as `G1`, `G2`, ...

        Returns
        -------
        solutions : [[int]]
            A list of all possible solutions. Each solution is itself a list
            of nodes.

        Raises
        ------
        NotImplementedError
            If the method is not implemented

        Notes
        -----
        The student's answer is compared against each path in the solutions until a match is found.
        The answer is only considered to be correct if the two lists are identical in size and order.
        i.e. an answer of [0, 1, 2] would fail against a list of solutions of [[0, 2, 1], [0, 1, 2, 3]].
        """
        raise NotImplementedError

    @abstractmethod
    def generate_feedback(self, graphs: list[nx.Graph], answer: list[int]) -> (bool, str):
        """Generates a message to be displayed when the solution has been submitted.

        Parameters
        ----------
        graphs: [networkx Graph]
            The networkx graphs used in the question.

        answer : [int]
            The student's choice of answer, a list of vertices.

        Returns
        -------
        (result, explanation) : (bool, str)
            A pair: whether the answer is correct, and the message to be displayed.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError


class QTextInput(Question):
    """Enter a text input value.

    The student can enter any string as their answer.

    Attributes
    ----------
    layout : str
        `"force-directed"` [default] | `"circle"` | `"grid"` | `"bipartite"`
        Determines the layout style for the graph.

    feedback : bool
        If `True`, use the `generate_feedback()` method,
        otherwise use the `generate_solutions()` method for verifying answers.

    node_prefix : str
        A prefix to prepend onto vertex labels.

    label_style : str
        `"none"` [default] | `"math"`
        Determines the style for node labels.

    data : None | any
        Persistent storage. You can set `data` to anything that is JSON serializable,
        and it will still be accessible if/when the `generate_feedback()` method is called.

    highlighted_nodes : None | list[int]
        A list of nodes to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    highlighted_edges : None | list[list[int, int]]
        A list of edges to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    data_type : str
        `"string"` [default] | `"integer"`
        If set to `"integer"`, client-side type-checking will be used to ensure the user only enters an integer value.
    """
    def __init__(self, layout='force-directed', feedback=False, node_prefix='', label_style='none', data=None,
                 highlighted_nodes=None, highlighted_edges=None, data_type='string'):
        super().__init__(layout=layout, feedback=feedback, node_prefix=node_prefix, label_style=label_style, data=data,
                         highlighted_nodes=highlighted_nodes, highlighted_edges=highlighted_edges)
        self.data_type = data_type

    @abstractmethod
    def generate_solutions(self, graphs: list[nx.Graph]) -> list[str]:
        """Generates a list of possible solutions.

        Each solution in the list should be a string that is an acceptable answer.
        The student's answer will be verified by comparing it with each solution until an equal string is found.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        Returns
        -------
        solutions : [str]
            A list of all possible solutions. Each solution is itself a string.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def generate_feedback(self, graphs: list[nx.Graph], answer: str) -> (bool, str):
        """Generates a message to be displayed when the solution has been submitted.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        answer : str
            The student's choice of answer, a string.

        Returns
        -------
        (result, explanation) : (bool, str)
            A pair: whether the answer is correct, and the message to be displayed.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError


class QMultipleChoice(Question):
    """Multiple choice question.

    This presents the student with a list of options to choose from.
    Depending on the `single_selection` setting, they will either be rendered as radio buttons or checkboxes.

    For this question type, the `generate_solutions` method *must* be implemented.
    This is because it is used to generate the actual multiple choice options.

    Attributes
    ----------
    layout : str
        `"force-directed"` [default] | `"circle"` | `"grid"` | `"bipartite"`
        Determines the layout style for the graph.

    feedback : bool
        If `True`, use the `generate_feedback()` method,
        otherwise use the `generate_solutions()` method for verifying answers.

    node_prefix : str
        A prefix to prepend onto vertex labels.

    label_style : str
        `"none"` [default] | `"math"`
        Determines the style for node labels.

    data : None | any
        Persistent storage. You can set `data` to anything that is JSON serializable,
        and it will still be accessible if/when the `generate_feedback()` method is called.

    highlighted_nodes : None | list[int]
        A list of nodes to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    highlighted_edges : None | list[list[int, int]]
        A list of edges to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    single_selection : bool
        If `True`, the user can only select a single option (i.e. radio button).
        Otherwise, the user can select multiple options (i.e. checkbox).
    """
    def __init__(self, layout='force-directed', feedback=False, node_prefix='', label_style='none', data=None,
                 highlighted_nodes=None, highlighted_edges=None, single_selection=False):
        super().__init__(layout=layout, feedback=feedback, node_prefix=node_prefix, label_style=label_style, data=data,
                         highlighted_nodes=highlighted_nodes, highlighted_edges=highlighted_edges)
        self.single_selection = single_selection

    @abstractmethod
    def generate_solutions(self, graphs: list[nx.Graph]) -> list[[str, bool]]:
        """Generates a list of the options for the question.

        This method *must* be implemented, regardless of the `feedback` setting.
        However, if `feedback` is set to `True`, the boolean values returned are irrelevant.
        This is because the `generate_feedback()` method will be used to verify the student's answer instead.

        When the options are shown to the student, they are all initialised to `False`, i.e. unselected.
        On submission, these truth values are compared to the ones you set here.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        Returns
        -------
        solutions : [[str, bool]]
            A list of possible solutions.
            Each solution is itself a pair: the unique text displayed for that option,
            and whether this option is a correct choice.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def generate_feedback(self, graphs: list[nx.Graph], answer: list[[str, bool]]) -> (bool, str):
        """Generates a message to be displayed when the solution has been submitted.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        answer : [[str, bool]]
            The student's choice of answer.
            This is a copy of the options generated by the `generate_solutions()` method,
            but with the student's selections represented as `True` values.

        Returns
        -------
        (result, explanation) : (bool, str)
            A pair: whether the answer is correct, and the message to be displayed.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError


class QVertexSet(Question):
    """Select a vertex set.

    The student selects a set of vertices in the graph by tapping on nodes.
    Their answer is represented as a list of nodes, e.g. `[5, 2, 7]`.

    Attributes
    ----------
    layout : str
        `"force-directed"` [default] | `"circle"` | `"grid"` | `"bipartite"`
        Determines the layout style for the graph.

    feedback : bool
        If `True`, use the `generate_feedback()` method,
        otherwise use the `generate_solutions()` method for verifying answers.

    node_prefix : str
        A prefix to prepend onto vertex labels.

    label_style : str
        `"none"` [default] | `"math"`
        Determines the style for node labels.

    data : None | any
        Persistent storage. You can set `data` to anything that is JSON serializable,
        and it will still be accessible if/when the `generate_feedback()` method is called.

    highlighted_nodes : None | list[int]
        A list of nodes to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    highlighted_edges : None | list[list[int, int]]
        A list of edges to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    selection_limit : int
        Maximum number of nodes the user is allowed to select.
        Default is `-1` (no limit).
    """
    def __init__(self, layout='force-directed', feedback=False, node_prefix='', label_style='none', data=None,
                 highlighted_nodes=None, highlighted_edges=None, selection_limit=-1,):
        super().__init__(layout=layout, feedback=feedback, node_prefix=node_prefix, label_style=label_style, data=data,
                         highlighted_nodes=highlighted_nodes, highlighted_edges=highlighted_edges)
        self.selection_limit = selection_limit

    @abstractmethod
    def generate_solutions(self, graphs: list[nx.Graph]) -> list[[int]]:
        """Generates a list of possible solutions.

        Each solution is itself a list of nodes.
        For example, the return value could be

        [[5, 2, 7],
         [1, 2, 6]]

        Indicating there are 2 possible solutions: the set `[5, 2, 7]` and the set `[1, 2, 6]`.

        The student's answer is verified by comparing it against each solution.
        The answer and solution are compared as sets, so order is irrelevant.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        Returns
        -------
        solutions : [[int]]
            A list of all possible solutions.
            Each solution is itself a list of nodes.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def generate_feedback(self, graphs: list[nx.Graph], answer: list[int]) -> (bool, str):
        """Generates a message to be displayed when the solution has been submitted.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        answer : [[int]]
            The student's choice of answer, a list of vertices.

        Returns
        -------
        (result, explanation) : (bool, str)
            A pair: whether the answer is correct, and the message to be displayed.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError


class QEdgeSet(Question):
    """Select a set of edges.

    The student selects edges by tapping on them in the graph.
    Their answer is represented as a list of pairs, e.g. `[[0, 1], [3, 4], [2, 3]]`.


    Attributes
    ----------
    layout : str
        `"force-directed"` [default] | `"circle"` | `"grid"` | `"bipartite"`
        Determines the layout style for the graph.

    feedback : bool
        If `True`, use the `generate_feedback()` method,
        otherwise use the `generate_solutions()` method for verifying answers.

    node_prefix : str
        A prefix to prepend onto vertex labels.

    label_style : str
        `"none"` [default] | `"math"`
        Determines the style for node labels.

    data : None | any
        Persistent storage. You can set `data` to anything that is JSON serializable,
        and it will still be accessible if/when the `generate_feedback()` method is called.

    highlighted_nodes : None | list[int]
        A list of nodes to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    highlighted_edges : None | list[list[int, int]]
        A list of edges to be highlighted in the graph with an underlay.
        If you update it within the `generate_feedback()` method,
        the changes will apply when displaying the feedback.

    selection_limit : int
        The maximum number of edges the user is allowed to select.
        Default is `-1` (no limit).
    """
    def __init__(self, layout='force-directed', feedback=False, node_prefix='', label_style='none', data=None,
                 highlighted_nodes=None, highlighted_edges=None, selection_limit=-1):
        super().__init__(layout=layout, feedback=feedback, node_prefix=node_prefix, label_style=label_style, data=data,
                         highlighted_nodes=highlighted_nodes, highlighted_edges=highlighted_edges)
        self.selection_limit = selection_limit

    @abstractmethod
    def generate_solutions(self, graphs: list[nx.Graph]) -> list[list[list[int, int]]]:
        """Generates a list of possible solutions.

        Each solution is itself a list of edge pairs.
        For example, the return value could be

        [[[0, 1], [3, 4], [2, 3]],
         [[0, 1], [2, 3]]]

        Indicating there are 2 possible solutions: the set of edges `[0, 1], [3, 4], [2, 3]`
        and the set of edges `[0, 1], [2, 3]`.

        The student's answer is verified by comparing it against each solution.
        The answer and solution are compared as sets, so order is irrelevant.
        When comparing individual edges, order is only important when the graph is directed.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        Returns
        -------
        solutions : [[[int, int]]]
            A list of all possible solutions.
            Each solution is a list of edge pairs.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def generate_feedback(self, graphs: list[nx.Graph], answer: list[list[int, int]]) -> (bool, str):
        """Generates a message to be displayed when the solution has been submitted.

        Parameters
        ----------
        graphs : [networkx Graph]
            The NetworkX graphs used in the question.

        answer : [[int, int]]
            The student's choice of answer, a list of edges.

        Returns
        -------
        (result, explanation) : (bool, str)
            A pair: whether the answer is correct, and the message to be displayed.

        Raises
        ------
        NotImplementedError
            If the method is not implemented
        """
        raise NotImplementedError
