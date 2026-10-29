from itertools import product

from pytest import raises

from nested_mapping.tools import match_keys
from nested_mapping.tools.match import (
    set_keys_consistent_left_in_right,
    set_keys_consistent_right_in_left,
    set_keys_consistent_symmetric,
    zip_match_keys_to_set_key,
)


def test_set_keys_consistent():
    ab = set("ab")
    abc = set("abc")
    abce = set("abce")
    abcd = set("abcd")
    abd = set("abd")
    abe = set("abe")
    ac = set("ac")
    empty = set()
    assert set_keys_consistent_symmetric(abc, abc) is True
    assert set_keys_consistent_symmetric(ab, abc) is True
    assert set_keys_consistent_symmetric(abc, ac) is True

    assert set_keys_consistent_symmetric(abcd, abce) is False
    assert set_keys_consistent_symmetric(abd, abce) is False
    assert set_keys_consistent_symmetric(abcd, abe) is False
    assert set_keys_consistent_symmetric(empty, abc) is True
    assert set_keys_consistent_symmetric(abc, empty) is True

    assert set_keys_consistent_left_in_right(abc, abc) is True
    assert set_keys_consistent_left_in_right(ab, abc) is True
    assert set_keys_consistent_left_in_right(abc, ac) is False

    assert set_keys_consistent_left_in_right(abcd, abce) is False
    assert set_keys_consistent_left_in_right(abd, abce) is False
    assert set_keys_consistent_left_in_right(abcd, abe) is False
    assert set_keys_consistent_left_in_right(empty, abc) is True
    assert set_keys_consistent_left_in_right(abc, empty) is False

    assert set_keys_consistent_right_in_left(abc, abc) is True
    assert set_keys_consistent_right_in_left(ab, abc) is False
    assert set_keys_consistent_right_in_left(abc, ac) is True

    assert set_keys_consistent_right_in_left(abcd, abce) is False
    assert set_keys_consistent_right_in_left(abd, abce) is False
    assert set_keys_consistent_right_in_left(abcd, abe) is False
    assert set_keys_consistent_right_in_left(empty, abc) is False
    assert set_keys_consistent_right_in_left(abc, empty) is True


def test_zip_match_keys_to_set_key():
    ab = tuple("ab")
    abc = tuple("abc")
    abce = tuple("abce")
    abcd = tuple("abcd")
    abd = tuple("abd")
    abe = tuple("abe")
    ac = tuple("ac")
    empty = tuple()

    assert list(
        zip_match_keys_to_set_key(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            abc,
            set(abc),
            keys_consistent_fcn=set_keys_consistent_symmetric,
        )
    ) == [(ab, abc), (abc, abc), (abce, abc), (abcd, abc), (ac, abc), (empty, abc)]

    assert list(
        zip_match_keys_to_set_key(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            abc,
            set(abc),
            keys_consistent_fcn=set_keys_consistent_left_in_right,
        )
    ) == [(ab, abc), (abc, abc), (ac, abc), (empty, abc)]


    assert list(
        zip_match_keys_to_set_key(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            abc,
            set(abc),
            keys_consistent_fcn=set_keys_consistent_right_in_left,
        )
    ) == [(abc, abc), (abce, abc), (abcd, abc)]


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
    match_keys((left,), right, print, fcn_on_skip=print_skip)
    print()

    print("left+(), right")
    match_keys((left, ((),)), right, print, fcn_on_skip=print_skip)
    print()

    print("left+left, right")
    match_keys((left, left), right, print, fcn_on_skip=print_skip)
    print()

    print("left+right, right")
    match_keys((left, right), right, print, fcn_on_skip=print_skip)
    print()

    print("left extra, right extra")
    match_keys(
        (left_extra,),
        right_extra,
        print,
        require_all_left_keys_processed=False,
        require_all_right_keys_processed=False,
        fcn_on_skip=print_skip,
    )
    print()

    print("left, right extra")
    match_keys(
        (left,),
        right_extra,
        print,
        require_all_left_keys_processed=False,
        require_all_right_keys_processed=False,
        fcn_on_skip=print_skip,
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
