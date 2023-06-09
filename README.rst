GraphQuest
==========

GraphQuest is a small Python library for creating graph theory question generators.
It is intended to be used in conjunction with the GraphQuest website,
where teachers can upload their question generators and build topics (i.e. quizzes) from them.

This library contains the following modules:

* `graph.py <https://github.com/PaoloMura/graphquest/blob/main/src/graphquest/graph.py>`_
    A module that provides additional features on top of networkx.
* `question.py <https://github.com/PaoloMura/graphquest/blob/main/src/graphquest/question.py>`_
    A module that contains all the question types that you can extend.

The GraphQuest repository can be found at `https://github.com/PaoloMura/graphquest <https://github.com/PaoloMura/graphquest>`_


Installation
------------

Use `pip <https://pypi.org/project/pip/>`_ to install the GraphQuest package:

.. code-block:: console

    $ pip install graphquest@git+https://github.com/PaoloMura/graphquest/


Usage
-----

Here's an example of the GraphQuest package being used to create a new question from the QVertexSet type.

.. code-block:: python

    # Import the question type you need.
    from graphquest.question import QVertexSet
    import networkx as nx
    import random

    # Extend the question type.
    class EvenDegrees(QVertexSet):
        def __init__(self):
            # Pass in settings to the parent's constructor.
            # The circle layout arranges nodes in a clockwise circle.
            super().__init__(layout="circle")

        def generate_data(self):
            # Return the networkx graph to be displayed.
            n = random.randint(5, 10)
            G = nx.gnp_random_graph(n, p=0.4)
            return G

        def generate_question(self, graph):
            # Return the wording of the question.
            return "Select all vertices with even degree."

        def generate_solutions(self, graph):
            # Return a list of all acceptable solutions.
            # Each solution must be a node value.
            solution = [n for (n, d) in graph.degree if d % 2 == 0]
            return [solution]

        def generate_feedback(self, graph, answer):
            # Leave this as a stub function, since we aren't providing detailed feedback.
            return ""
