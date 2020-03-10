from brightway2 import *
import warnings
from .utils import ParameterNameGenerator
from presamples.models.parameterized import ParameterizedBrightwayModel as PBM
from numpy import inf
import copy

class ActivityLandBalancer():
    """Balances land exchange samples at the activity level

    Upon instantiation, will identify and classify all land exchanges.
    New generic parameter names are also generated for each land exchange.

    Use Method `generate_samples` to actually generate samples. This is usually
    invoked via a DatabaseLandBalancer instance.

    Parameters:
    ------------
       act_key: tuple
           Key of the activity.
       database_land_balancer: DatabaseLandBalancer
           Instance of a DatabaseLandBalancer

    """

    def __init__(self, act_key, database_land_balancer):
        self.act = get_activity(act_key)
        for keys in [
            'land_in_keys', 'land_out_keys',
            'all_land_keys', 'group'
        ]:
            setattr(self, keys, getattr(database_land_balancer, keys))
        land_exchanges = [
            exc for exc in self.act.exchanges()
            if exc.input.key in self.all_land_keys
        ]
        if not land_exchanges:
            self.strategy = "skip"
            self.land_exchanges = land_exchanges
        else:
            self._move_exchange_formulas_to_temp()
            self.land_exchanges = [
                exc for exc in self.act.exchanges()
                if exc.input.key in self.all_land_keys
            ]
            self.land_exchange_input_keys = [exc.input.key for exc in self.land_exchanges]
            self.land_exchange_types = [self._get_type(exc) for exc in self.land_exchanges]
            namer = ParameterNameGenerator()
            self.land_exchange_param_names = [namer['land_param'] for _ in range(len(self.land_exchanges))]
            self.activity_params = []

    def generate_samples(self, iterations=1000):
        """Calls other methods in order and adds parameters to group

        Parameters:
        ------------
           iterations: int
               Number of iterations in sample.
        """

        if not self._processed():
            self.parameters = []
            self._identify_strategy()
            self._define_balancing_parameters()
        if self.strategy == 'skip':
            return []

        self._move_land_formulas_to_exchange()
        self._move_activity_parameters_to_temp()
        parameters.new_activity_parameters(self.activity_params, self.group)
        parameters.add_exchanges_to_group(self.group, self.act)
        parameters.recalculate()
        pbm = PBM(self.group)
        pbm.load_parameter_data()
        pbm.calculate_stochastic(iterations, update_amounts=True)
        pbm.calculate_matrix_presamples()
        self.matrix_data = pbm.matrix_data
        parameters.remove_from_group(self.group, self.act)
        # This adds activity parameters that are actually not wanted. Remove them.
        self.act['parameters'] = []
        self.act.save()
        self.activity_params = []
        self._restore_activity_parameters()
        self._restore_exchange_formulas()
        return self.matrix_data

    def _identify_strategy(self):
        """Identify appropriate strategy to use for activity"""

        land_out = [
            exc for i, exc in enumerate(self.land_exchanges)
            if self.land_exchange_types[i] == 'land_out'
        ]
        land_in = [
            exc for i, exc in enumerate(self.land_exchanges)
            if self.land_exchange_types[i] == 'land_in'
        ]

        # Identify non-zero exchanges
        non_zero_in = [exc for exc in land_in if exc['amount'] != 0]
        non_zero_out = [exc for exc in land_out if exc['amount'] != 0]

        # If there isn't at least one non-zero input land exchange and one non-zero
        # output land exchange, skip
        if any([not non_zero_in, not non_zero_out]):
            self.strategy = "skip"
            return

        # Identify land exchanges with uncertainty
        exc_with_uncertainty_inputs = [exc for exc in land_in if exc.get('uncertainty type', 0) != 0]
        exc_with_uncertainty_outputs = [exc for exc in land_out if exc.get('uncertainty type', 0) != 0]

        # If there aren't any uncertain land exchanges, skip
        if len(exc_with_uncertainty_inputs + exc_with_uncertainty_outputs) == 0:
            self.strategy = "skip"
        # If there is only one uncertain land exchange, set_static
        elif len(exc_with_uncertainty_inputs + exc_with_uncertainty_outputs) == 1:
            self.strategy = "set_static"
        # If there are no uncertain inputs, inverse strategy (i.e. rescale outputs)
        elif len(exc_with_uncertainty_inputs) == 0:
            self.strategy = "inverse"
        # Apply default strategy otherwise (i.e. rescale inputs)
        else:
            self.strategy = "default"

    def _define_balancing_parameters(self):
        """Define activity-level and exchange-level parameters for rebalancing

        The actual equations used for rebalancing depends on the associated strategy.
        """

        if self.strategy == 'skip':
            return
        if self.strategy == 'default':
            self._get_static_data_default()
        if self.strategy == 'inverse':
            self._get_static_data_inverse()
        if self.strategy == 'set_static':
            self._get_static_data_set_static()

    def _get_static_data_default(self):
        """Define activity-level and exchange-level parameters for default rebalancing

        Rebalancing based on rescaling variable inputs so that the ratio of
        inputs to outputs is equal to the same ratio in the static activity.
        """
        var_in_terms = []
        const_in_terms = []
        out_terms = []
        in_total = 0
        out_total = 0

        for i, exc in enumerate(self.land_exchanges):
            param_name = self.land_exchange_param_names[i]
            land_exchange_type = self.land_exchange_types[i]
            exc_amount_value = exc.get('amount', 0)
            exc_amount_string = self.land_exchange_param_names[i]
            if land_exchange_type == 'land_in':
                # add amount to appropriate total for calculating ratio and balance
                in_total += exc_amount_value
                # generate term for ratio equation
                term = exc_amount_string
                # add exchange to activity parameters (exchange parameter will
                # simply hook to this parameter)
                self.activity_params.append(self.convert_exchange_to_param(exc, param_name))
                if exc.get('uncertainty type', 0) != 0:
                    # Add term to variable portion of inputs
                    var_in_terms.append(term)
                    # Add hook to exchange, with scaling
                    exc['formula'] = "{} * scaling".format(param_name)
                    exc.save()
                else:
                    # Add term to constant portion of inputs
                    const_in_terms.append(term)
                    # Add hook to exchange, without scaling (constant)
                    exc['formula'] = param_name
                    exc.save()
            elif land_exchange_type == 'land_out':
                out_total += exc_amount_value
                # generate term for ratio equation
                term = exc_amount_string
                out_terms.append(term)
                # Add hook to exchange
                exc['formula'] = param_name
                exc.save()
                # Add parameter to activity parameters
                self.activity_params.append(self.convert_exchange_to_param(exc, param_name))

        self.in_total = in_total
        self.out_total = out_total
        self.static_ratio = in_total / out_total if out_total!=0 else inf
        self.static_balance = in_total - out_total
        self.activity_params.append(
            {
                'name': 'static_ratio',
                'database': exc.output['database'],
                'code': exc.output['code'],
                'amount': self.static_ratio,
                'uncertainty type': 0,
                'loc': self.static_ratio,
            }
        )
        out_term = self._get_term(out_terms)
        const_in_term = self._get_term(const_in_terms, on_empty=0)
        var_in_term = self._get_term(var_in_terms)
        self.activity_params.append(
            {
                'name': 'scaling',
                'formula': "({}*{}-{})/({})".format(self.static_ratio, out_term, const_in_term, var_in_term),
                'database': exc.output['database'],
                'code': exc.output['code'],
            },
        )
        self.activity_params.append(
            {
                'name': 'ratio',
                'formula': "(scaling * {} + {})/{}".format(var_in_term, const_in_term, out_term),
                'database': exc.output['database'],
                'code': exc.output['code'],
            },
        )

    def _get_static_data_inverse(self):
        """Define activity-level and exchange-level parameters for inverse rebalancing

        Rebalancing based on rescaling variable outputs so that the ratio of
        outputs to inputs is equal to the same ratio in the static activity.

        """
        var_out_terms = []
        const_out_terms = []
        in_terms = []
        in_total = 0
        out_total = 0

        for i, exc in enumerate(self.land_exchanges):
            param_name = self.land_exchange_param_names[i]
            land_exchange_type = self.land_exchange_types[i]
            exc_amount_value = exc.get('amount', 0)
            exc_amount_string = self.land_exchange_param_names[i]
            if land_exchange_type == 'land_out':
                # add amount to appropriate total for calculating ratio and balance
                out_total += exc_amount_value
                # generate term for ratio equation
                term = exc_amount_string
                # add exchange to activity parameters (exchange parameter will
                # simply hook to this parameter)
                self.activity_params.append(self.convert_exchange_to_param(exc, param_name))
                if exc.get('uncertainty type', 0) != 0:
                    # Add term to variable portion of inputs
                    var_out_terms.append(term)
                    # Add hook to exchange, with scaling
                    exc['formula'] = "{} * scaling".format(param_name)
                    exc.save()
                else:
                    # Add term to constant portion of inputs
                    const_out_terms.append(term)
                    # Add hook to exchange, without scaling (constant)
                    exc['formula'] = param_name
                    exc.save()
            elif land_exchange_type == 'land_in':
                in_total += exc_amount_value
                # generate term for ratio equation
                term = exc_amount_string
                in_terms.append(term)
                # Add hook to exchange
                exc['formula'] = param_name
                exc.save()
                # Add parameter to activity parameters
                self.activity_params.append(self.convert_exchange_to_param(exc, param_name))

        self.in_total = in_total
        self.out_total = out_total
        self.static_ratio = out_total / in_total
        self.static_balance = out_total - in_total
        self.activity_params.append(
            {
                'name': 'static_ratio',
                'database': exc.output['database'],
                'code': exc.output['code'],
                'amount': self.static_ratio,
                'uncertainty type': 0,
                'loc': self.static_ratio,
            }
        )
        in_term = self._get_term(in_terms)
        const_out_term = self._get_term(const_out_terms, 0)
        var_out_term = self._get_term(var_out_terms, min_terms=2)
        self.activity_params.append(
            {
                'name': 'scaling',
                'formula': "({}*{}-{})/{}".format(self.static_ratio, in_term, const_out_term, var_out_term),
                'database': exc.output['database'],
                'code': exc.output['code'],
            },
        )
        self.activity_params.append(
            {
                'name': 'ratio',
                'formula': "(scaling * {} + {})/{}".format(var_out_term, const_out_term, in_term),
                'database': exc.output['database'],
                'code': exc.output['code'],
            },
        )

    def _get_static_data_set_static(self):
        """Define activity-level and exchange-level parameter to replace variable data with static data array
        """
        excs = [
            exc for exc in self.act.exchanges()
            if exc.input.key in self.all_land_keys
               and exc.get('uncertainty type', 0) != 0
        ]
        if len(excs) != 1:
            raise ValueError("Should only have one variable land exchange for 'set_static' strategy")
        exc = excs[0]
        exc['formula'] = 'cst'
        exc.save()
        self.static_ratio = 'Not calculated'
        self.static_balance = 'Not calculated'
        self.activity_params.append(self.convert_exchange_to_param(exc, 'cst'))
        self.activity_params[0]['uncertainty type'] = 0
        self.activity_params[0]['loc'] = exc['amount']

    def convert_exchange_to_param(self, exc, p_name):
        """ Convert exchange to formatted parameter dict"""
        param = {
            'name': p_name,
            'amount': exc.get('amount', 0),
            'uncertainty type': exc.get('uncertainty type', 0),
            'loc': exc.get('loc', exc.get('amount', 0)),
            'scale': exc.get('scale'),
            'negative': exc.get('negative', False),
            'database': self.act.get('database'),
            'code': self.act.get('code'),
        }
        if exc.get('minimum') is not None:
            param['minimum'] = exc.get('minimum')
        if exc.get('maximum') is not None:
            param['maximum'] = exc.get('maximum')
        return param

    def _get_term(self, terms, on_empty=None, min_terms=None):
        """Translate a set of string terms to a single term to use in a formula """
        if min_terms is not None and len(terms) < min_terms :
            raise ValueError(
                "Expected at least {} terms, got {}".format(
                    min_terms, len(terms)
                )
            )
        if len(terms) == 0 and on_empty is None:
            raise ValueError("At least one term is needed for this strategy")
        elif len(terms) == 0:
            return str(on_empty)
        elif len(terms) == 1:
            return "{}".format(terms[0])
        else:
            return "({})".format(" + ".join(terms))

    def _get_type(self, exc):
        """Return type of exchange"""
        input_key = exc.input.key
        if input_key in self.land_in_keys:
            return 'land_in'
        elif input_key in self.land_out_keys:
            return 'land_out'
        else:
            warnings.warn(
                "Exchange type not understood for exchange "
                "between {} and {} ({}), not considered in balance.".format(
                    exc.input.key, exc.output.key, exc.get('type')
                ))
            return 'skip'

    def _reset(self):
        """Reset attributes"""
        self.strategy = None
        self.static_ratio = None
        self.static_balance = None
        self.activity_params = []

    def _processed(self):
        """ Return True if strategy, ratio and parameters already identified"""
        if getattr(self, 'strategy', None) is None:
            return False
        if self.strategy == 'skip':
            return True
        if any([
            getattr(self, 'static_ratio', None) is None,
            getattr(self, 'static_balance', None) is None,
            not getattr(self, 'activity_params', None),
            ]):
            return False
        return True

    def _move_exchange_formulas_to_temp(self):
        """ Temporarily move existing formulas to avoid conflicts

        Existing formulas are moved from `formulas` to `temp_formulas` so they
        don't get picked up by `new_activity_parameters` later.
        In fact, ecoinvent formulas often referred to chemical formulas for
        biosphere exchanges.

        Formulas can be restored with the `_restore_exchange_formulas` method.
        """
        for exc in self.act.exchanges():
            if 'formula' in exc:
                exc['temp_formula'] = exc['formula']
                del exc['formula']
                exc.save()

    def _move_land_formulas_to_exchange(self):
        """ Move land balance formulas to formulas field"""
        for exc in self.act.exchanges():
            if 'land_formula' in exc:
                exc['formula'] = exc['land_formula']
                exc.save()

    def _move_activity_parameters_to_temp(self):
        """ Temporarily move existing activity parameters to avoid conflicts

        Existing parameters are moved from `act.parameters` to `act.temp_formulas`
        so they don't get picked up by `new_activity_parameters` later.

        Parameters can be restored with the `_restore_activity_parameters` method.
        """
        self.act['parameters_temp'] = copy.copy(self.act.get('parameters'))
        self.act['parameters'] = []
        self.act.save()

    def _restore_activity_parameters(self):
        """ Restore activity parameters that were temporarily removed

        Should be done once done working with the activity.
        """
        self.act['parameters'] = self.act.get('parameters_temp')
        del self.act['parameters_temp']
        self.act.save()

    def _restore_exchange_formulas(self):
        """ Restore exchange formulas that were temporarily removed

        Also moves formulas used for land balancing to 'land_formulas'
        Should be done once done working with the activity.
        """
        for exc in self.act.exchanges():
            if 'formula' in exc:
                exc['land_formula'] = copy.copy(exc.get('formula', None))
                del exc['formula']
            if 'temp_formula' in exc:
                exc['formula'] = exc.get('temp_formula', None)
                del exc['temp_formula']
            exc.save()
