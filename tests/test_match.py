from itertools import product

from pytest import raises

from nested_mapping.tools import match_keys
from nested_mapping.tools.match import (
    keys_consistent_left_in_right,
    keys_consistent_right_in_left,
    keys_consistent_symmetric,
)


def test_keys_consistent():
    assert keys_consistent_symmetric(set("abc"), set("abc")) is True
    assert keys_consistent_symmetric(set("ab"), set("abc")) is True
    assert keys_consistent_symmetric(set("abc"), set("ac")) is True

    assert keys_consistent_symmetric(set("abcd"), set("abce")) is False
    assert keys_consistent_symmetric(set("abd"), set("abce")) is False
    assert keys_consistent_symmetric(set("abcd"), set("abe")) is False

    assert keys_consistent_left_in_right(set("abc"), set("abc")) is True
    assert keys_consistent_left_in_right(set("ab"), set("abc")) is True
    assert keys_consistent_left_in_right(set("abc"), set("ac")) is False

    assert keys_consistent_left_in_right(set("abcd"), set("abce")) is False
    assert keys_consistent_left_in_right(set("abd"), set("abce")) is False
    assert keys_consistent_left_in_right(set("abcd"), set("abe")) is False

    assert keys_consistent_right_in_left(set("abc"), set("abc")) is True
    assert keys_consistent_right_in_left(set("ab"), set("abc")) is False
    assert keys_consistent_right_in_left(set("abc"), set("ac")) is True

    assert keys_consistent_right_in_left(set("abcd"), set("abce")) is False
    assert keys_consistent_right_in_left(set("abd"), set("abce")) is False
    assert keys_consistent_right_in_left(set("abcd"), set("abe")) is False


def test_match():
    i1 = ("1", "2", "3")
    i2 = ("A", "B", "C")
    i3 = ("x", "y", "z")

    right = tuple((a, b) for a, b in product(i1, i2))
    left = tuple((a,) for a, in i2)

    right_extra = tuple((a, b) for a, b in product(i1, i2))
    left_extra = tuple((a, b) for a, b in product(i1, i3))

    def print_skip(i, key_left, key_right):
        print(f"skip {i} {key_left} {key_right}")

    print("left")
    print(left)

    print("right")
    print(right)

    print("left_extra")
    print(left_extra)

    print("right_extra")
    print(right_extra)

    print("left, right")
    match_keys((left,), right, print, fcn_skip=print_skip)
    print()

    print("left+(), right")
    match_keys((left, ((),)), right, print, fcn_skip=print_skip)
    print()

    print("left+left, right")
    match_keys((left, left), right, print, fcn_skip=print_skip)
    print()

    print("left+right, right")
    match_keys((left, right), right, print, fcn_skip=print_skip)
    print()

    print("left extra, right extra")
    match_keys(
        (left_extra,),
        right_extra,
        print,
        require_all_left_keys_processed=False,
        require_all_right_keys_processed=False,
        fcn_skip=print_skip,
    )
    print()

    print("left, right extra")
    match_keys(
        (left,),
        right_extra,
        print,
        require_all_left_keys_processed=False,
        require_all_right_keys_processed=False,
        fcn_skip=print_skip,
    )
    print()

    with raises(ValueError):
        match_keys((left_extra,), right_extra, print)

    print()


def test_match_partial():
    i1 = ("1", "2", "3")
    i2 = ("A", "B", "C")

    left1 = tuple(i1)
    left2 = tuple((a, b) for a, b in product(i1, i2[:-1]))
    left3 = tuple(i2)
    right = tuple((a, b) for a, b in product(i1, i2))

    def print_before(*args):
        print(f"befr", *args)

    def print_after(*args):
        print(f"aftr", *args)

    def print_skip(i, key_left, key_right):
        print("skip", f"{i} {key_left} {key_right}")

    def print_proc(i, key_left, key_right):
        print(f"proc {i} {key_left} {key_right}")

    print("left1")
    print(left1)

    print("left2")
    print(left2)

    print("left3")
    print(left3)

    print("right")
    print(right)
    print()

    print("(left1, left2, left3), right: exception)")
    with raises(ValueError):
        match_keys(
            (left1, left2, left3),
            right,
            print_proc,
            # fcn_outer_before=print_before,
            # fcn_outer_after=print_after,
            # fcn_skip=print_skip
        )
    print()

    print("(left1, left2, left3), right: allow")
    match_keys(
        (left1, left2, left3),
        right,
        print_proc,
        require_all_left_keys_match_right=False,
        # fcn_outer_before=print_before,
        # fcn_outer_after=print_after,
        # fcn_skip=print_skip
    )
    print()
