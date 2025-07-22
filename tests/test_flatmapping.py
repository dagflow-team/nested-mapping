from itertools import permutations

from nestedmapping.flatmapping import FlatMapping
from pytest import raises


def test_getset():
    flatmapping = FlatMapping()
    safeflatmapping = FlatMapping(protect=True)
    val = "val"
    val2 = ["val", "lav"]
    flatmapping["a", "b", "c"] = val
    safeflatmapping["a", "b", "c"] = val
    for key in permutations(("a", "b", "c")):
        assert flatmapping[tuple(key)] == val
        assert safeflatmapping[tuple(key)] == val
    flatmapping["c", "b", "a"] = val2
    for key in permutations(("a", "b", "c")):
        assert flatmapping[tuple(key)] == val2
        with raises(AttributeError):
            safeflatmapping[tuple(key)] = val2
    safeflatmapping._protect = False
    for key in permutations(("a", "b", "c")):
        safeflatmapping[tuple(key)] = val


def test_slice_filter():
    flatmapping = FlatMapping()
    flatmapping["a", "b"] = 1
    flatmapping["a", "b", "c"] = 2
    flatmapping["a", "c", "d", "b"] = 3
    assert all(
        len(tuple(x)) == 3
        for x in (flatmapping.items(), flatmapping.items("a"), flatmapping.items("a", "b"))
    )
    assert len(tuple(flatmapping.items("a", "b", "c"))) == 2
    assert len(tuple(flatmapping.items("a", "b", "d", "c"))) == 1
    assert isinstance(flatmapping.slice("a"), FlatMapping)
    assert all(
        x == flatmapping
        for x in (
            flatmapping.slice("a"),
            flatmapping.slice("a", "b"),
            flatmapping.slice(
                filterkey=lambda key: all(elem in "abcd" for elem in key)
            ),
            flatmapping.slice(filterkeyelem=lambda key: key in "abcd")
        )
    )
    assert flatmapping.slice("a", "b", "c") == {
        ("a", "b", "c"): 2,
        ("a", "b", "c", "d"): 3,
    }
    assert flatmapping.slice("a", "b", "c", "d") == {
        ("a", "b", "c", "d"): 3,
    }
    assert flatmapping.slice(
        filterkey=lambda key: all(elem != "d" for elem in key)
    ) == {
        ("a", "b", "c"): 2,
        ("a", "b"): 1,
    }

def test_merge():
    fd = FlatMapping()
    fdsub = FlatMapping()
    fdsub['d', 'e', 'f'] = 3
    fdsub['d', 'e', 'g'] = 4

    fd['a', 'b', 'c1'] = 1
    fd['a', 'b', 'c2'] = 2
    fd['a', 'b', 'c4'] = fdsub

    assert fd['a', 'b', 'c1'] == 1
    assert fd['a', 'b', 'c2'] == 2
    fd['a', 'b', 'c4', 'd', 'e', 'f'] = 3
    fd['a', 'b', 'c4', 'd', 'e', 'g'] = 4
