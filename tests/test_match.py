from itertools import product

from pytest import raises

from nested_mapping.tools import match_keys
from nested_mapping.tools.match import (
    match_keys_to_key,
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
    x = tuple("x")
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

    assert list(
        zip_match_keys_to_set_key(
            [ab, abc, abce, abcd, abd, abe, ac],
            x,
            set(x),
            keys_consistent_fcn=set_keys_consistent_symmetric,
        )
    ) == []


def test_match_keys_to_set_key():
    ab = tuple("ab")
    abc = tuple("abc")
    abce = tuple("abce")
    abcd = tuple("abcd")
    abd = tuple("abd")
    abe = tuple("abe")
    ac = tuple("ac")
    x = tuple("x")
    empty = tuple()

    def call_match(left, right, tright, cmp):
        accepted, rejected = [], []
        rejected_left_keys, accepted_left_keys = set(), set()
        rejected_right_keys, accepted_right_keys = set(), set()

        def fcn_take(left, right):
            accepted.append((left, right))

        def fcn_reject(left, right):
            rejected.append((left, right))

        right_accepted = match_keys_to_key(
            left,
            right,
            tright,
            cmp,
            fcn_take,
            fcn_on_reject=fcn_reject,
            collect_rejected_left_keys=True,
            collect_rejected_right_keys=True,
            rejected_left_keys=rejected_left_keys,
            rejected_right_keys=rejected_right_keys,
            accepted_left_keys=accepted_left_keys,
            accepted_right_keys=accepted_right_keys,
        )

        return (
            right_accepted,
            accepted,
            rejected,
            rejected_left_keys,
            accepted_left_keys,
            rejected_right_keys,
            accepted_right_keys,
        )

    (
        right_accepted,
        accepted,
        rejected,
        rejected_left_keys,
        processed_left_keys,
        rejected_right_keys,
        processed_right_keys,
    ) = call_match(
        [ab, abc, abce, abcd, abd, abe, ac, empty],
        abc,
        set(abc),
        set_keys_consistent_symmetric,
    )
    assert right_accepted==True
    assert accepted == [(ab, abc), (abc, abc), (abce, abc), (abcd, abc), (ac, abc), (empty, abc)]
    assert rejected == [(abd, abc), (abe, abc)]
    assert rejected_left_keys == {abd, abe}
    assert processed_left_keys == {ab, abc, abce, abcd, ac, empty}
    assert rejected_right_keys == set()
    assert processed_right_keys == {abc}

    (
        right_accepted,
        accepted,
        rejected,
        rejected_left_keys,
        processed_left_keys,
        rejected_right_keys,
        processed_right_keys,
    ) = call_match(
        [ab, abc, abce, abcd, abd, abe, ac, empty],
        abc,
        set(abc),
        set_keys_consistent_left_in_right,
    )
    assert right_accepted==True
    assert accepted == [(ab, abc), (abc, abc), (ac, abc), (empty, abc)]
    assert rejected == [(abce, abc), (abcd, abc), (abd, abc), (abe, abc)]
    assert rejected_left_keys == {abd, abce, abcd, abe}
    assert processed_left_keys == {ab, abc, ac, empty}
    assert rejected_right_keys == set()
    assert processed_right_keys == {abc}

    (
        right_accepted,
        accepted,
        rejected,
        rejected_left_keys,
        processed_left_keys,
        rejected_right_keys,
        processed_right_keys,
    ) = call_match(
        [ab, abc, abce, abcd, abd, abe, ac, empty],
        abc,
        set(abc),
        set_keys_consistent_right_in_left,
    )
    assert right_accepted==True
    assert accepted == [(abc, abc), (abce, abc), (abcd, abc)]
    assert rejected == [(ab, abc), (abd, abc), (abe, abc), (ac, abc), (empty, abc)]
    assert rejected_left_keys == {ab, abd, abe, ac, empty}
    assert processed_left_keys == {abc, abce, abcd}
    assert rejected_right_keys == set()
    assert processed_right_keys == {abc}

    (
        right_accepted,
        accepted,
        rejected,
        rejected_left_keys,
        processed_left_keys,
        rejected_right_keys,
        processed_right_keys,
    ) = call_match(
        [ab, abc, abce, abcd, abd, abe, ac],
        x,
        set(x),
        set_keys_consistent_symmetric,
    )
    assert right_accepted==False
    assert accepted == []
    assert rejected == [(ab, x), (abc, x), (abce, x), (abcd, x), (abd, x), (abe, x), (ac, x)]
    assert rejected_left_keys == {ab, abc, abce, abcd, abd, abe, ac}
    assert processed_left_keys == set()
    assert rejected_right_keys == {x}
    assert processed_right_keys == set()


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
    match_keys((left,), right, print, fcn_on_reject=print_skip)
    print()

    print("left+(), right")
    match_keys((left, ((),)), right, print, fcn_on_reject=print_skip)
    print()

    print("left+left, right")
    match_keys((left, left), right, print, fcn_on_reject=print_skip)
    print()

    print("left+right, right")
    match_keys((left, right), right, print, fcn_on_reject=print_skip)
    print()

    print("left extra, right extra")
    match_keys(
        (left_extra,),
        right_extra,
        print,
        require_all_left_keys_accepted=False,
        require_all_right_keys_accepted=False,
        fcn_on_reject=print_skip,
    )
    print()

    print("left, right extra")
    match_keys(
        (left,),
        right_extra,
        print,
        require_all_left_keys_accepted=False,
        require_all_right_keys_accepted=False,
        fcn_on_reject=print_skip,
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
