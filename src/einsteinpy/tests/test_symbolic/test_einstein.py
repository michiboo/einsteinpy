import numpy as np
import pytest
import sympy
from sympy import cos, simplify, sin, sinh, tensorcontraction

from einsteinpy.symbolic import EinsteinTensor, MetricTensor, RicciScalar


def schwarzschild_metric():
    symbolstr = "t r theta phi"
    syms = sympy.symbols(symbolstr)
    G, M, c, a = sympy.symbols("G M c a")
    # using metric values of schwarschild space-time
    # a is schwarzschild radius
    list2d = np.zeros((4, 4), dtype=int).tolist()
    list2d[0][0] = 1 - (a / syms[1])
    list2d[1][1] = -1 / ((1 - (a / syms[1])) * (c ** 2))
    list2d[2][2] = -1 * (syms[1] ** 2) / (c ** 2)
    list2d[3][3] = -1 * (syms[1] ** 2) * (sympy.sin(syms[2]) ** 2) / (c ** 2)
    sch = MetricTensor(list2d, syms)
    return sch


def anti_de_sitter_metric():
    coords = sympy.symbols("t chi theta phi")
    t, ch, th, ph = coords
    m = sympy.diag(
        -1,
        cos(t) ** 2,
        cos(t) ** 2 * sinh(ch) ** 2,
        cos(t) ** 2 * sinh(ch) ** 2 * sin(th) ** 2,
    ).tolist()
    metric = MetricTensor(m, coords)
    return metric


def test_EinsteinTensor_ValueError_wrong_config_length():
    testarr = np.ones((4, 4), dtype=int).tolist()
    syms = sympy.symbols("x y")
    try:
        obj = EinsteinTensor(testarr, syms, config="lll", parent_metric=None)
        assert False
    except ValueError:
        assert True


@pytest.mark.parametrize("metric", [anti_de_sitter_metric(), schwarzschild_metric()])
def test_EinsteinTensor_trace_negetive_of_Ricci_Scalar_in_4D(metric):
    # https://en.wikipedia.org/wiki/Einstein_tensor#Trace
    G1 = EinsteinTensor.from_metric(metric)
    G2 = G1.change_config("ul")
    val1 = simplify(tensorcontraction(G2.tensor(), (0, 1)))
    val2 = RicciScalar.from_metric(metric).expr
    assert simplify(val1 + val2) == 0


def test_EinsteinTensor_symbols_parent_metric_wrong_change_config():
    metric = anti_de_sitter_metric()
    G = EinsteinTensor.from_metric(metric)
    assert G.parent_metric == G._parent_metric and G.parent_metric == metric
    assert G.symbols() == G.syms and G.symbols() == metric.symbols()
    G._parent_metric = None
    try:
        obj = G.change_config("ul")
        boolstore = False
    except Exception:
        boolstore = True
    assert boolstore
