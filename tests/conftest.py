import pytest
from bw2data.tests import bw2test
from brightway2 import Database, projects
from shutil import rmtree
import numpy as np

@pytest.fixture
@bw2test
def data_for_testing():
    # Make sure we are starting off with an empty project
    assert not len(Database('test_db'))
    assert not len(Database('biosphere'))

    biosphere = Database("biosphere")
    biosphere.register()
    biosphere.write({
        ("biosphere", "Transformation, from 1"): {
            'categories': ('natural resource', 'land'),
            'exchanges': [],
            'name': 'Transformation, from 1',
            'type': 'natural resource',
            'unit': 'square meter'
        },
        ("biosphere", "Transformation, from 2"): {
            'categories': ('natural resource', 'land'),
            'exchanges': [],
            'name': 'Transformation, from 2',
            'type': 'natural resource',
            'unit': 'square meter'
        },
        ("biosphere", "Transformation, to 1"): {
            'categories': ('natural resource', 'land'),
            'exchanges': [],
            'name': 'Transformation, to 1',
            'type': 'natural resource',
            'unit': 'square meter'
        },
        ("biosphere", "Transformation, to 2"): {
            'categories': ('natural resource', 'land'),
            'exchanges': [],
            'name': 'Transformation, to 2',
            'type': 'natural resource',
            'unit': 'square meter'
        },
        ("biosphere", "Something else"): {
            'categories': ['air'],
            'exchanges': [],
            'name': 'Something else to air, in m3',
            'type': 'emission',
            'unit': 'kg'
        },
    })
    assert len(Database('biosphere')) == 5

    test_db = Database("test_db")
    test_db.register()
    test_db.write({
        ("test_db", "X"): {
            'name': 'X',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "A"): {
            'name': 'A',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'A'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, from 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1,
                    'formula': 'some_formula'
                },
                {
                    'name': 'Transformation, from 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, from 2'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, to 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, to 1'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                    'loc': 1.0,
                },
                {
                    'name': 'Transformation, to 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, to 2'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "B"): {
            'name': 'B',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'B'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, from 1'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, from 2'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, to 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, to 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, to 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, to 2'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "C"): {
            'name': 'C',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'C'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 1',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, from 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, from 2',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Transformation, from 2'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(4.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, to 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, to 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, to 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, to 2'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Something else, to air',
                    'unit': 'kilogram',
                    'amount': 100.0,
                    'input': ("biosphere", "Something else"),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(100.0),
                    'scale': 0.1
                },
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "D"): {
            'name': 'D',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'inverse',
                'ratio': 2,
                'balance': 20
            },
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'D'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 1',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, from 1'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 2',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Transformation, from 2'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, to 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, to 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, to 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, to 2'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "G"): {
            'name': 'G',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'G'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, from 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, from 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, from 2'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, to 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, to 1'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, to 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, to 2'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "H"): {
            'name': 'H',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'set_static',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'H'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, from 1'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, from 2'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, to 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, to 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, to 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, to 2'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "I"): {
            'name': 'I',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'skip',
                'ratio': None,
                'balance': -20
            },
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'I'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, to 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, to 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1

                },
                {
                    'name': 'Transformation, to 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, to 2'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
            ],
        },
        ("test_db", "J"): {
            'name': 'J',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'J'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, from 1'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Transformation, from 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, from 2'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "K"): {
            'name': 'K',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'some product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'skip',
                'ratio': None,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'some product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'K'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, from 1'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, from 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, from 2'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, to 1',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Transformation, to 1'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Transformation, to 2',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Transformation, to 2'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
            ],
        },
    })
    yield {'project': projects.current}

    rmtree(projects.dir, ignore_errors=True)