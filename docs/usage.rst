Usage
=====

.. _installation:

Installation
------------

To use Graph Quest, first install it using pip:

.. code-block:: console

   (.venv) $ pip install graphquest@git+https://github.com/PaoloMura/graphquest/


.. _creating_questions:

Creating questions
------------------

To get started, create a Python file and import the question type.

.. code-block:: python
    :lineno-start: 1

    from graphquest.question import QTextInput

Alternatively, import all question types.

.. code-block:: python
    :lineno-start: 1

    from graphquest.question import *

Now create a Python class that extends this class and implements its methods.

.. code-block:: python
    :lineno-start: 2

    import networkx as nx
    import random

    class MyQuestion(QTextInput):
        def __init__(self):
            super().__init__()

        def generate_data(self):
            n = random.randint(5, 10)
            G = nx.gnp_random_graph(n, p=0.4)
            return [G]

        def generate_question(self, graphs):
            return 'How many nodes does this graph have?'

        def generate_solutions(self, graphs):
            num_nodes = graphs[0].number_of_nodes()
            return [str(num_nodes)]

        def generate_feedback(self, graphs, answer):
            return True, ''

All question types have four methods you must implement:

* `generate_data()` - returns a list of graphs to be displayed
* `generate_question(graphs)` - returns the wording of the question
* `generate_solutions(graphs)` - returns a list of accepted solutions
* `generate_feedback(graphs, answer)` - returns whether the given answer is correct, together with an explanation

There are currently five supported question types in Graph Quest:

* `QTextInput` (answer via a text box)
* `QMultipleChoice` (answer by selecting options)
* `QVertexSet` (answer by tapping on nodes in the graph)
* `QEdgeSet` (answer by tapping on edges in the graph)
* `QSelectPath` (answer by tapping nodes in a valid order in the graph)

See :ref:`the examples <example_question_types>` for how each question type is displayed.

.. note::

    The data type used for the answer is different for each question type.
    `QTextInput` and `QMultipleChoice` allow for multiple graphs to be displayed side by side,
    which will be labelled as G1, G2, ....
    The other question types only allow a single NetworkX graph to be used in the question
    (however this may include multiple components).


.. _generating_answer_feedback:

Generating Answer Feedback
--------------------------

Only one of `generate_solutions()` and `generate_feedback()` should be implemented.

`generate_solutions()` creates a list of accepted solutions before the student is given the question.
The student's answer is then compared against this list for verification.

Alternatively, you can implement the `generate_feedback()` method.
This waits for the student to answer first, then takes in their answer as a parameter.
It processes the answer—together with the original graphs used in the question—to verify their answer.
This provides an opportunity to return an additional feedback string, which could be unique to the student's answer.

By default, only `generate_solutions()` is used (see the :ref:`example above <creating_questions>`).

To use the `generate_feedback()` method instead, first specify that you want the `generate_feedback()` method to be used.

.. code-block:: python
    :lineno-start: 7
    :name: python_feedback_setting

    super().__init__(feedback=True)

Now implement this function and leave `generate_solutions()` as a stub function.

.. code-block:: python
    :lineno-start: 17

    def generate_solutions(graphs):
        return []

    def generate_feedback(graphs, answer):
        num_nodes = graphs[0].number_of_nodes()
        if int(answer) < num_nodes:
            return False, f"Too low! The correct answer is {num_nodes}"
        elif int(answer) > num_nodes:
            return False, f"Too high! The correct answer is {num_nodes}"
        else:
            return True, ""

For specific information on the data types that should be used for each question type, see the :doc:`api` section.

See also the :ref:`question_lifecycle` section.

.. note::

    For the QMultipleChoice question type, the `generate_solutions()` method is always used
    as a way of specifying the options for the answer.
    The `generate_feedback()` method is still optional.


Question Settings
-----------------

Constructor arguments are used to specify question settings.

The `layout` setting determines the layout algorithm used to display the graphs.
The options are:

* `force-directed` (node positions are determined after applying 'forces' to them);
* `circle` (nodes are arranged in a clockwise circle in order of their value);
* `grid` (nodes are arranged in a grid);
* `bipartite` (nodes are assigned to one of two columns).
* `tree` (nodes are arranged in a hierarchical structure based on a breadth-first traversal).

.. note::

    For bipartite layouts, each node in the graph should be given a `bipartite` attribute set to either `0` or `1`.
    This is done automatically when using bipartite graph generators in networkx.

The `data` setting gives persistent storage.
It will retain its value when the `generate_feedback()` method is called.
For more information on its relevance, see the :ref:`next section <question_lifecycle>`.

The `highlight_nodes` and `highlight_edges` settings may be used to provide a list of elements
to be highlighted with a blue underlay in the graph.
These attributes may be changed in the `generate_feedback()` method,
and when the feedback is shown to the student,
those elements will also be highlighted in the graph to aid your explanation.

All settings can be changed at any time within the class methods.
See the :ref:`next section <question_lifecycle>` to understand exactly when the values will be used.

See the :ref:`code above <python_feedback_setting>` for an example with the `feedback` setting.

See the :doc:`api` section for a list of available settings for each question type.


.. _question_lifecycle:

Question Lifecycle
------------------

The sequence of events is as follows.

1. An object of the question class is instantiated.
2. The `generate_data()` method is called.
3. The `generate_question()` method is called.
4. If the `feedback` setting is `False`, the `generate_solutions()` method is called.
5. The settings are extracted from the object's attributes.
6. The generated data is sent with the settings to the student.
7. The student answers the question.
8. If the `feedback` setting is `False`, their answer is verified against the list of solutions.
9. Otherwise, another object of the question class is instantiated.
Their answer is processed by its `generate_feedback()` method and the explanation is shown to them.
Any updates to `highlight_nodes` and `highlight_edges` settings are captured.

.. note::

    When the graphs are passed to each method, a deepcopy is used.
    This means you are free to modify the graphs themselves if you like.
