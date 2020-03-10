import pytest
import numpy as np
from bw2landbalancer.database_land_balancer import DatabaseLandBalancer
from bw2landbalancer.activity_land_balancer import ActivityLandBalancer
from brightway2 import get_activity

def get_matrix_data_sums_for_test(ab, matrix_data):
    """Function to check matrix data in tests

    Should be called after generate_samples
    """
    samples_to_concat = []
    md_indices_inputs = []
    for md in matrix_data:
        md_indices_inputs.extend([i[0] for i in md[1]])
        samples_to_concat.append(md[0])
    indices_order = [md_indices_inputs.index(exc) for exc in ab.land_exchange_input_keys]
    samples = np.concatenate(samples_to_concat, axis=0)[indices_order]
    out_filter = np.array(
        [1 if ab.land_exchange_types[i] == 'land_out' else 0 for i, exc in enumerate(ab.land_exchanges)]
    ).reshape(-1, 1)
    in_filter = np.array(
        [1 if ab.land_exchange_types[i] == 'land_in' else 0 for i, exc in enumerate(ab.land_exchanges)]
    ).reshape(-1, 1)
    in_totals = np.sum(in_filter * samples, axis=0)
    out_totals = np.sum(out_filter * samples, axis=0)
    return in_totals, out_totals

def test_no_such_database(data_for_testing):
    with pytest.raises(ValueError, match="Database no such db not imported"):
        wb = DatabaseLandBalancer(database_name="no such db")


def test_no_such_biosphere(data_for_testing):
    with pytest.raises(ValueError, match="Database no such biosphere not imported"):
        wb = DatabaseLandBalancer(database_name="test_db", biosphere="no such biosphere")


def test_identify_exchanges(data_for_testing):
    """Find and classify all land transformation elementary flows in biosphere"""

    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    expected_land_in_keys = [
        ("biosphere", "Transformation, from 1"),
        ("biosphere", "Transformation, from 2"),
    ]
    expected_land_out_keys = [
        ("biosphere", "Transformation, to 1"),
        ("biosphere", "Transformation, to 2"),
    ]

    expected_all_keys = expected_land_in_keys + expected_land_out_keys

    assert set(wb.land_in_keys) == set(expected_land_in_keys)
    assert len(wb.land_in_keys) == len(expected_land_in_keys)
    assert set(wb.land_out_keys) == set(expected_land_out_keys)
    assert len(wb.land_out_keys) == len(expected_land_out_keys)
    assert set(wb.all_land_keys) == set(expected_all_keys)
    assert len(wb.all_land_keys) == len(expected_all_keys)

def test_land_exchange_formulas_removed(data_for_testing):
    """ Make sure formulas are properly removed from exchanges"""
    act = get_activity(("test_db", "A"))
    exc = [exc for exc in act.exchanges() if exc.input.key==('biosphere', 'Transformation, from 1')][0]
    assert exc['formula']=='some_formula'
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'A'), wb)
    exc = [exc for exc in ab.act.exchanges() if exc.input.key == ('biosphere', 'Transformation, from 1')][0]
    assert exc.get('formula', 'Nothing')=='Nothing'

def test_initially_unprocessed(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'A'), wb)
    assert not ab._processed()
    ab._identify_strategy()
    assert not ab._processed()
    ab._define_balancing_parameters()
    assert ab._processed()


def test_reset(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'A'), wb)
    ab._identify_strategy()
    ab._define_balancing_parameters()
    assert ab._processed()
    ab._reset()
    assert not ab._processed()
    assert getattr(ab, "static_ratio") is None
    assert getattr(ab, "static_balance") is None
    assert getattr(ab, "activity_params") == []

def test_rebalance_default_ratio_1(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    assert wb.matrix_indices == []
    assert wb.matrix_samples is None
    ab = ActivityLandBalancer(('test_db', 'A'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert len(matrix_data) == 1
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 4
    in_sum, out_sum = get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)
    wb.add_samples_for_act(ab.act, 5)
    assert len(wb.matrix_indices)==4
    assert wb.matrix_samples.shape[0] == 4
    assert wb.matrix_samples.shape[1] == 5

def test_rebalance_inverse_ratio_1(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'B'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'inverse'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 1
    assert ab.static_balance == 0
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 4
    in_sum, out_sum = get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(out_sum/in_sum, ab.static_ratio)

def test_rebalance_default_ratio_2(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'C'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'default'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 2
    assert ab.static_balance == 3
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 4
    in_sum, out_sum = get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(in_sum/out_sum, ab.static_ratio)

def test_rebalance_inverse_ratio_2(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'D'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'inverse'
    ab._define_balancing_parameters()
    assert ab.static_ratio == 0.5
    assert ab.static_balance == -3
    matrix_data = ab.generate_samples(5)
    assert matrix_data[0][0].shape[1]==5
    assert matrix_data[0][0].shape[0] == 4
    in_sum, out_sum = get_matrix_data_sums_for_test(ab, matrix_data)
    assert np.allclose(out_sum/in_sum, ab.static_ratio)

def test_rebalance_set_static_one_input(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'G'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'set_static'
    exc_initial = [
        exc for exc in ab.act.exchanges()
        if exc.input.key == ("biosphere", "Transformation, from 1")
    ][0]
    assert exc_initial.get('uncertainty type', 0) == 2
    assert exc_initial.get('loc', 0) == np.log(exc_initial['amount'])

    ab._define_balancing_parameters()
    assert getattr(ab, "static_ratio") == "Not calculated"
    assert getattr(ab, "static_balance") == "Not calculated"
    exc_after = [
        exc for exc in ab.act.exchanges()
        if exc.input.key == ("biosphere", "Transformation, from 1")
    ][0]
    assert exc_after.get('formula', 0) == 'cst'
    assert ab.activity_params[0]['name'] == 'cst'
    assert ab.activity_params[0]['amount'] == exc_initial['amount']
    assert ab.activity_params[0]['loc'] == exc_initial['amount']
    assert ab.activity_params[0]['uncertainty type'] == 0
    matrix_data = ab.generate_samples(5)
    assert len(matrix_data)==1
    assert matrix_data[0][0].shape[1]==5
    assert matrix_data[0][0].shape[0]==1
    assert np.allclose(np.ones(shape=(1, 5)), matrix_data[0][0])
    assert len(matrix_data[0][1]) == 1
    assert matrix_data[0][1][0] == (("biosphere", "Transformation, from 1"), ('test_db', 'G'))

def test_rebalance_set_static_one_output(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'H'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'set_static'
    exc_initial = [
        exc for exc in ab.act.exchanges()
        if exc.input.key == ("biosphere", "Transformation, to 1")
    ][0]
    assert exc_initial.get('uncertainty type', 0) == 2
    assert exc_initial.get('loc', 0) == np.log(exc_initial['amount'])

    ab._define_balancing_parameters()
    assert getattr(ab, "static_ratio", "Nope") == "Not calculated"
    assert getattr(ab, "static_balance", "Nope") == "Not calculated"
    exc_after = [
        exc for exc in ab.act.exchanges()
        if exc.input.key == ("biosphere", "Transformation, to 1")
    ][0]
    assert exc_after.get('formula', 0) == 'cst'
    assert ab.activity_params[0]['name'] == 'cst'
    assert ab.activity_params[0]['amount'] == exc_initial['amount']
    assert ab.activity_params[0]['loc'] == exc_initial['amount']
    assert ab.activity_params[0]['uncertainty type'] == 0
    matrix_data = ab.generate_samples(5)
    assert len(matrix_data) == 1
    assert matrix_data[0][0].shape[1] == 5
    assert matrix_data[0][0].shape[0] == 1
    assert np.allclose(np.ones(shape=(1, 5)), matrix_data[0][0])
    assert len(matrix_data[0][1]) == 1
    assert matrix_data[0][1][0] == (("biosphere", "Transformation, to 1"), ('test_db', 'H'))


def test_rebalance_skip_no_input(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'I'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'skip'
    assert ab._processed()
    assert getattr(ab, "static_ratio", "Nope") is "Nope"
    assert getattr(ab, "static_balance", "Nope") is "Nope"
    assert ab.generate_samples() == []


def test_rebalance_skip_no_output(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'J'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'skip'
    assert getattr(ab, "static_ratio", "Nope") is "Nope"
    assert getattr(ab, "static_balance", "Nope") is "Nope"


def test_rebalance_skip_no_uncertainty(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    ab = ActivityLandBalancer(('test_db', 'K'), wb)
    ab._identify_strategy()
    assert ab.strategy == 'skip'
    assert getattr(ab, "static_ratio", "Nope") is "Nope"
    assert getattr(ab, "static_balance", "Nope") is "Nope"


def test_all_matrix_data_and_presamples(data_for_testing):
    """ """
    wb = DatabaseLandBalancer(database_name="test_db", biosphere="biosphere")
    assert wb.matrix_indices==[]
    assert wb.matrix_samples is None
    wb.add_samples_for_all_acts(5)
    assert len(wb.matrix_indices)==18
    assert wb.matrix_samples.shape == (18, 5)
    id_, dirpath = wb.create_presamples(id_="test")
    indices_0 = np.load(dirpath/"{}.0.indices.npy".format(id_))
    samples_0 = np.load(dirpath/"{}.0.samples.npy".format(id_))
    assert indices_0.shape[0] == 18
    assert samples_0.shape[1] == 5
