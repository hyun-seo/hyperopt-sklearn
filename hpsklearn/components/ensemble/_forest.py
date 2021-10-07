from ._base import validate

from hyperopt.pyll import scope
from hyperopt import hp

from sklearn import ensemble
import numpy as np

import typing


@scope.define
def sklearn_RandomForestClassifier(*args, **kwargs):
    return ensemble.RandomForestClassifier(*args, **kwargs)


@scope.define
def sklearn_RandomForestRegressor(*args, **kwargs):
    return ensemble.RandomForestRegressor(*args, **kwargs)


@scope.define
def sklearn_ExtraTreesClassifier(*args, **kwargs):
    return ensemble.ExtraTreesClassifier(*args, **kwargs)


@scope.define
def sklearn_ExtraTreesRegressor(*args, **kwargs):
    return ensemble.ExtraTreesRegressor(*args, **kwargs)


def _forest_classifier_criterion(name):
    """
    Declaration of search space 'criterion' parameter for
     random forest classifier
     extra trees classifier
    """
    return hp.choice(name, ["gini", "entropy"])


def _random_forest_regressor_criterion(name):
    """
    Declaration of search space 'criterion' parameter for
     random forest regressor

    Parameter 'poisson' is also available. Not implemented since
     'poisson' is only available for non-negative y data
    """
    return hp.choice(name, ["squared_error", "absolute_error"])


def _extra_trees_regressor_criterion(name):
    """
    Declaration of search space 'criterion' parameter for
     extra trees regressor
    """
    return hp.choice(name, ["squared_error", "absolute_error"])


def _forest_n_estimators(name):
    """
    Declaration search space 'n_estimators' parameter
    """
    return scope.int(hp.qloguniform(name, np.log(9.5), np.log(3000.5), 1))


def _forest_max_depth(name):
    """
    Declaration search space 'max_depth' parameter
    """
    return hp.pchoice(name, [
        (0.7, None),  # most common choice.
        (0.1, 2),  # try some shallow trees.
        (0.1, 3),
        (0.1, 4),
    ])


def _forest_min_samples_split(name):
    """
    Declaration search space 'min_samples_split' parameter
    """
    return hp.pchoice(name, [
        (0.95, 2),  # most common choice
        (0.05, 3),  # try minimal increase
    ])


def _forest_min_samples_leaf(name):
    """
    Declaration search space 'min_samples_leaf' parameter
    """
    return hp.choice(name, [
        1,  # most common choice.
        scope.int(hp.qloguniform(name + ".gt1", np.log(1.5), np.log(50.5), 1))
    ])


def _forest_min_weight_fraction_leaf(name):
    """
    Declaration search space 'min_weight_fraction_leaf' parameter
    """
    return 0.0


def _forest_max_features(name):
    """
    Declaration search space 'max_features' parameter
    """
    return hp.pchoice(name, [
        (0.2, "sqrt"),  # most common choice.
        (0.1, "log2"),  # less common choice.
        (0.1, None),  # all features, less common choice.
        (0.6, hp.uniform(name + ".frac", 0., 1.))
    ])


def _forest_max_leaf_nodes(name):
    """
    Declaration search space 'max_leaf_nodes' parameter
    """
    return hp.pchoice(name, [
        (0.85, None),  # most common choice
        (0.05, 5),
        (0.05, 10),
        (0.05, 15),
    ])


def _forest_min_impurity_decrease(name):
    """
    Declaration search space 'min_impurity_decrease' parameter
    """
    return hp.pchoice(name, [
        (0.85, 0.0),  # most common choice
        (0.05, 0.01),
        (0.05, 0.02),
        (0.05, 0.05),
    ])


def _forest_bootstrap(name):
    """
    Declaration search space 'bootstrap' parameter
    """
    return hp.choice(name, [True, False])


def _forest_random_state(name):
    """
    Declaration search space 'random_state' parameter
    """
    return hp.randint(name, 5)


@validate(params=["max_features"],
          validation_test=lambda param: isinstance(param, str) and param not in ["auto", "sqrt", "log2"],
          msg="Invalid parameter '%s' with value '%s'. Value must be in ['auto', 'sqrt', 'log2'].")
@validate(params=["n_estimators", "max_depth", "min_samples_split",
                  "min_samples_leaf", "max_features", "max_leaf_nodes",
                  "min_impurity_decrease"],
          validation_test=lambda param: isinstance(param, float) and not param > 0,
          msg="Invalid parameter '%s' with value '%s'. Parameter value must be non-negative and greater than 0.")
@validate(params=["ccp_alpha"],
          validation_test=lambda param: isinstance(param, float) and not param < 0,
          msg="Invalid parameter '%s' with value '%s'. Parameter value must be non-negative.")
def _forest_hp_space(
        name_func,
        n_estimators: int = None,
        max_depth: int = None,
        min_samples_split: float = None,
        min_samples_leaf: float = None,
        min_weight_fraction_leaf: float = None,
        max_features: typing.Union[str, float] = None,
        max_leaf_nodes: int = None,
        min_impurity_decrease: float = None,
        bootstrap: bool = None,
        oob_score: bool = False,
        n_jobs: int = 1,
        random_state=None,
        verbose: int = False,
        warm_start: bool = False,
        ccp_alpha: float = 0.0,
        max_samples: float = None
):
    """
    Hyper parameter search space for
     random forest classifier
     random forest regressor
     extra trees classifier
     extra trees regressor
    """
    if bootstrap is False and any([oob_score, max_samples]) is not None:
        raise ValueError("Invalid declaration of parameters. \n"
                         "For usage of custom parameters 'oob_score' and 'max_samples' "
                         "parameter 'bootstrap' can not be False.")
    hp_space = dict(
        n_estimators=(n_estimators or _forest_n_estimators(name_func("n_estimators"))),
        max_depth=(_forest_max_depth(name_func("max_depth"))
                   if max_depth is None else max_depth),
        min_samples_split=(min_samples_split or _forest_min_samples_split(name_func("min_samples_split"))),
        min_samples_leaf=(min_samples_leaf or _forest_min_samples_leaf(name_func("min_samples_leaf"))),
        min_weight_fraction_leaf=(min_weight_fraction_leaf
                                  or _forest_min_weight_fraction_leaf(name_func("min_weight_fraction_leaf"))),
        max_features=(max_features or _forest_max_features(name_func("max_features"))),
        max_leaf_nodes=(_forest_max_leaf_nodes(name_func("max_leaf_nodes"))
                        if max_leaf_nodes is None else max_leaf_nodes),
        min_impurity_decrease=(min_impurity_decrease
                               or _forest_min_impurity_decrease(name_func("min_impurity_decrease"))),
        bootstrap=(_forest_bootstrap(name_func("bootstrap")) if bootstrap is None else bootstrap),
        oob_score=oob_score,
        n_jobs=n_jobs,
        random_state=_forest_random_state(name_func("random_state")) if random_state is None else random_state,
        verbose=verbose,
        warm_start=warm_start,
        ccp_alpha=ccp_alpha,
        max_samples=max_samples
    )
    return hp_space


def random_forest_classifier(name: str, criterion: str = None, **kwargs):
    """
    Return a pyll graph with hyperparameters that will construct
    a sklearn.ensemble.RandomForestClassifier model.

    Args:
        name: name | str
        criterion: choose 'gini' or 'entropy' | str

    See help(hpsklearn.components.ensemble._forest._forest_hp_space)
    for info on additional available random forest/extra trees arguments.
    """

    def _name(msg):
        return f"{name}.rfc_{msg}"

    hp_space = _forest_hp_space(_name, **kwargs)
    hp_space["criterion"] = (criterion or _forest_classifier_criterion(_name("criterion")))

    return scope.sklearn_RandomForestClassifier(**hp_space)


def random_forest_regressor(name: str, criterion: str = None, **kwargs):
    """
    Return a pyll graph with hyperparameters that will construct
    a sklearn.ensemble.RandomForestRegressor model.

    Args:
        name: name | str
        criterion: 'squared_error', 'mse', 'absolute_error', 'poisson' | str

    See help(hpsklearn.components.ensemble._forest._forest_hp_space)
    for info on additional available random forest/extra trees arguments.
    """

    def _name(msg):
        return f"{name}.rfr_{msg}"

    hp_space = _forest_hp_space(_name, **kwargs)
    hp_space["criterion"] = (criterion or _random_forest_regressor_criterion(_name("criterion")))

    return scope.sklearn_RandomForestRegressor(**hp_space)


def extra_trees_classifier(name: str, criterion: str = None, **kwargs):
    """
    Return a pyll graph with hyperparameters that will construct
    a sklearn.ensemble.ExtraTreesClassifier model.

    Args:
        name: name | str
        criterion: 'gini', 'entropy' | str

    See help(hpsklearn.components.ensemble._forest._forest_hp_space)
    for info on additional available random forest/extra trees arguments.
    """

    def _name(msg):
        return f"{name}.etc_{msg}"

    hp_space = _forest_hp_space(_name, **kwargs)
    hp_space["criterion"] = (criterion or _forest_classifier_criterion(_name("criterion")))

    return scope.sklearn_ExtraTreesClassifier(**hp_space)


def extra_trees_regressor(name: str, criterion: str = None, **kwargs):
    """
    Return a pyll graph with hyperparameters that will construct
    a sklearn.ensemble.ExtraTreesRegressor model.

    Args:
        name: name | str
        criterion: 'squared_error', 'mse', 'absolute_error', 'mae' | str

    See help(hpsklearn.components.ensemble._forest._forest_hp_space)
    for info on additional available random forest/extra trees arguments.
    """

    def _name(msg):
        return f"{name}.etr_{msg}"

    hp_space = _forest_hp_space(_name, **kwargs)
    hp_space["criterion"] = (criterion or _extra_trees_regressor_criterion(_name("criterion")))

    return scope.sklearn_ExtraTreesRegressor(**hp_space)


def _forest_classifiers(name):
    """
    All _forest classifiers

    Args:
        name: name | str
    """
    return [
        random_forest_classifier(name + ".random_forest"),
        extra_trees_classifier(name + ".extra_trees")
    ]


def _forest_regressors(name):
    """
    All _forest regressors

    Args:
        name: name | str
    """
    return [
        random_forest_regressor(name + ".random_forest"),
        extra_trees_regressor(name + ".extra_trees")
    ]
