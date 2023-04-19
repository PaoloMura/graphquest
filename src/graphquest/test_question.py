import argparse
import importlib
import inspect
import networkx as nx
import random
from question import Question
import string


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', nargs='?', help='filepath to be tested')
parser.add_argument('-v', '--verbose', nargs='?', default=True, help='whether to print additional output')
args = parser.parse_args()

def __load_module(filepath: str):
    """Load the specified Python module dynamically"""
    filepath = filepath.replace('.py', '').replace('/', '.')
    importlib.invalidate_caches()

    try:
        mod = importlib.import_module(filepath)
        return mod

    except ModuleNotFoundError as e:
        raise e

def __get_questions(filepath: str) -> [str]:
    """Returns the question classes within the given file"""
    mod = __load_module(filepath)

    def is_class(x):
        return inspect.isclass(x) and x.__module__ == mod.__name__

    try:
        classes = [getattr(mod, name) for name, _
                   in inspect.getmembers(mod, is_class)
                   if issubclass(getattr(mod, name), Question)]
        return classes

    except AttributeError as e:
        raise e


def __valid_type(q_type):
    accepted_types = ['QTextInput',
                      'QMultipleChoice',
                      'QVertexSet',
                      'QEdgeSet',
                      'QSelectPath']
    return q_type in accepted_types


def __random_string():
    letters = string.printable
    length = random.randint(0, 30)
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


def __validate_solution_type(sol, q_type):
    if q_type == 'QTextInput':
        assert isinstance(sol, str), 'generate_solutions() must return a list[str]'
    elif q_type == 'QMultipleChoice':
        assert isinstance(sol, list), 'generate_solutions() must return a list[list[str, bool]]'
        assert len(sol) == 2, 'generate_solutions() must return a list[list[str, bool]]'
        assert isinstance(sol[0], str), 'generate_solutions() must return a list[list[str, bool]]'
        assert isinstance(sol[1], bool), 'generate_solutions() must return a list[list[str, bool]]'
    elif q_type in ['QVertexSet', 'QSelectPath']:
        assert isinstance(sol, list), 'generate_solutions() must return a list[list[int]]'
        for item in sol:
            assert isinstance(item, int), 'generate_solutions() must return a list[list[int]]'
    elif q_type == 'QEdgeSet':
        assert isinstance(sol, list), 'generate_solutions() must return a list[list[list[int, int]]]'
        for item in sol:
            assert isinstance(item, list), 'generate_solutions() must return a list[list[list[int, int]]]'
            assert len(item) == 2, 'generate_solutions() must return a list[list[list[int, int]]]'
            assert isinstance(item[0], int), 'generate_solutions() must return a list[list[list[int, int]]]'
            assert isinstance(item[1], int), 'generate_solutions() must return a list[list[list[int, int]]]'
    else:
        assert False, 'Invalid question type'


def __validate_generate_solutions(q, q_type, gs):
    # Test it has a generate_solutions method
    assert hasattr(q, 'generate_solutions'), 'Class must implement generate_solutions()'
    assert callable(getattr(q, 'generate_solutions')), 'Class must implement generate_solutions()'

    # Test the generate_solutions method has the correct signature
    sig = inspect.signature(q.generate_solutions)
    assert len(sig.parameters) == 1, 'generate_solutions() must take in a list[networkx.Graph] parameter'

    # Test the generate_solutions return type
    sols = q.generate_solutions(gs)
    assert isinstance(sols, list), 'generate_solutions() must return a list of solutions'
    for sol in sols:
        __validate_solution_type(sol, q_type)


def __make_dummy_answer(q, q_type, gs):
    if q_type == 'QTextInput':
        if q.data_type == 'integer':
            return random.randint(-1000, 1000)
        else:
            return __random_string()
    elif q_type == 'QMultipleChoice':
        __validate_generate_solutions(q, q_type, gs)
        sols = q.generate_solutions(gs)
        return [[opt, random.choice([True, False])] for opt, _ in sols]
    elif q_type == 'QVertexSet':
        k = random.randint(0, len(gs[0].nodes))
        xs = random.sample(gs[0].nodes, k)
        random.shuffle(xs)
        return xs
    elif q_type == 'QEdgeSet':
        k = random.randint(0, len(gs[0].edges))
        xs = random.sample(gs[0].edges, k)
        xs = [list(x) for x in xs]
        random.shuffle(xs)
        return xs
    elif q_type == 'QSelectPath':
        n = len(gs[0].nodes)
        return list(nx.generate_random_paths(gs[0], 1, n))[0]
    else:
        assert False, 'Invalid question type'


answer_type = {
    'QTextInput': 'str',
    'QMultipleChoice': 'list[list[str, bool]]',
    'QVertexSet': 'list[int]',
    'QEdgeSet': 'list[list[int, int]]',
    'QSelectPath': 'List[int]'
}


def __validate_question(q):
    if args.verbose:
        print(f'Testing {type(q).__name__}...')

    # Test the class type is valid
    q_type = type(q).__bases__[0].__name__
    assert __valid_type(q_type), 'Class must derive from a Question base'

    if args.verbose:
        print('\tTesting generate_data()...', end='\t')

    # Test it has a generate_data method
    assert hasattr(q, 'generate_data'), 'Class must implement generate_data()'
    assert callable(getattr(q, 'generate_data')), 'Class must implement generate_data()'

    # Test the generate_data method has the correct signature
    sig = inspect.signature(q.generate_data)
    assert len(sig.parameters) == 0, 'generate_data() should not take in any parameters'

    # Test the generate_data return type
    gs = q.generate_data()
    assert isinstance(gs, list), 'generate_data() must return a list[networkx.Graph]'
    for g in gs:
        assert isinstance(g, nx.Graph), 'generate_data() must return a list[networkx.Graph]'

    if args.verbose:
        print('pass!')
        print('\tTesting generate_question()...', end='\t')

    # Test it has a generate_question method
    assert hasattr(q, 'generate_question'), 'Class must implement generate_question()'
    assert callable(getattr(q, 'generate_question')), 'Class must implement generate_question()'

    # Test the generate_question method has the correct signature
    sig = inspect.signature(q.generate_question)
    assert len(sig.parameters) == 1, 'generate_data() must take in a list[networkx.Graph] parameter'

    # Test the generate_question return type
    question = q.generate_question(gs)
    assert isinstance(question, str), 'generate_question() must return a str'

    if args.verbose:
        print('pass!')

    if q.feedback:
        if args.verbose:
            print('\tTesting generate_feedback()...', end='\t')

        # Test it has a generate_feedback method
        assert hasattr(q, 'generate_feedback'), 'Class must implement generate_feedback()'
        assert callable(getattr(q, 'generate_feedback')), 'Class must implement generate_feedback()'

        # Test the generate_feedback method has the correct signature
        sig = inspect.signature(q.generate_feedback)
        assert len(sig.parameters) == 2, f'generate_data() must take in a list[networkx.Graph] and {answer_type[q_type]} as parameters'

        # Test the generate_feedback return type
        ans = __make_dummy_answer(q, q_type, gs)
        result = q.generate_feedback(gs, ans)
        assert isinstance(result, tuple), 'generate_solutions() must return a tuple[bool, str]'
        assert len(result) == 2, 'generate_solutions() must return a tuple[bool, str]'
        assert isinstance(result[0], bool), 'generate_solutions() must return a tuple[str, str]'
        assert isinstance(result[1], str), 'generate_solutions() must return a tuple[bool, str]'

        if args.verbose:
            print('pass!')
    else:
        if args.verbose:
            print('\tTesting generate_feedback()...', end='\t')
        __validate_generate_solutions(q, q_type, gs)
        if args.verbose:
            print('pass!')


def test_file(filepath='', verbose=True):
    """Test all the question classes in the given file"""
    if filepath != '':
        q_classes = __get_questions(filepath)
        args.verbose = verbose
    else:
        q_classes = __get_questions(args.file)
    for cls in q_classes:
        obj = cls()
        __validate_question(obj)
    if args.verbose:
        print('All tests pass!')

def test_class(cls: type):
    """Test the given question class"""
    obj = cls()
    __validate_question(obj)
    if args.verbose:
        print('All tests pass!')


if __name__ == '__main__':
    test_file()
