from itertools import product

from pytest import raises

from nested_mapping.tools import match_keys
from nested_mapping.tools.match import (
    match_keys_to_key,
    set_keys_consistent_left_in_right,
    set_keys_consistent_right_in_left,
    set_keys_consistent_symmetric,
    zip_match_keys_to_key,
    zip_match_keys_to_keys,
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


def test_zip_match_keys_to_key():
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
        zip_match_keys_to_key(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            abc,
            set(abc),
            keys_consistent_fcn=set_keys_consistent_symmetric,
        )
    ) == [(ab, abc), (abc, abc), (abce, abc), (abcd, abc), (ac, abc), (empty, abc)]

    assert list(
        zip_match_keys_to_key(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            abc,
            set(abc),
            keys_consistent_fcn=set_keys_consistent_left_in_right,
        )
    ) == [(ab, abc), (abc, abc), (ac, abc), (empty, abc)]

    assert list(
        zip_match_keys_to_key(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            abc,
            set(abc),
            keys_consistent_fcn=set_keys_consistent_right_in_left,
        )
    ) == [(abc, abc), (abce, abc), (abcd, abc)]

    assert (
        list(
            zip_match_keys_to_key(
                [ab, abc, abce, abcd, abd, abe, ac],
                x,
                set(x),
                keys_consistent_fcn=set_keys_consistent_symmetric,
            )
        )
        == []
    )


def test_zip_match_keys_to_keys():
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
        zip_match_keys_to_keys(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            [abc, abd, x],
            keys_consistent_fcn=set_keys_consistent_symmetric,
        )
    ) == [
        (ab, abc),
        (abc, abc),
        (abce, abc),
        (abcd, abc),
        (ac, abc),
        (empty, abc),
        (ab, abd),
        (abcd, abd),
        (abd, abd),
        (empty, abd),
        (empty, x),
    ]

    assert list(
        zip_match_keys_to_keys(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            [abc, abd, x],
            keys_consistent_fcn=set_keys_consistent_left_in_right,
        )
    ) == [
        (ab, abc),
        (abc, abc),
        (ac, abc),
        (empty, abc),
        (ab, abd),
        (abd, abd),
        (empty, abd),
        (empty, x),
    ]

    assert list(
        zip_match_keys_to_keys(
            [ab, abc, abce, abcd, abd, abe, ac, empty],
            [abc, abd, x],
            keys_consistent_fcn=set_keys_consistent_right_in_left,
        )
    ) == [
        (abc, abc),
        (abce, abc),
        (abcd, abc),
        (abcd, abd),
        (abd, abd),
    ]


def test_match_keys_to_key():
    ab = tuple("ab")
    abc = tuple("abc")
    abce = tuple("abce")
    abcd = tuple("abcd")
    abd = tuple("abd")
    abe = tuple("abe")
    ac = tuple("ac")
    x = tuple("x")
    empty = tuple()

    def call_match(left, right, tright, cmp, **kwargs):
        processed, skipped = [], []
        skipped_left_keys, processed_left_keys = set(), set()
        skipped_right_keys, processed_right_keys = set(), set()

        def fcn_take(left, right):
            processed.append((left, right))

        def fcn_reject(left, right):
            skipped.append((left, right))

        right_processed = match_keys_to_key(
            left,
            right,
            tright,
            cmp,
            fcn_take,
            fcn_on_reject=fcn_reject,
            collect_skipped_left_keys=True,
            collect_skipped_right_keys=True,
            skipped_left_keys=skipped_left_keys,
            skipped_right_keys=skipped_right_keys,
            processed_left_keys=processed_left_keys,
            processed_right_keys=processed_right_keys,
            **kwargs,
        )

        return (
            right_processed,
            processed,
            skipped,
            skipped_left_keys,
            processed_left_keys,
            skipped_right_keys,
            processed_right_keys,
        )

    (
        right_processed,
        processed,
        skipped,
        skipped_left_keys,
        processed_left_keys,
        skipped_right_keys,
        processed_right_keys,
    ) = call_match(
        [ab, abc, abce, abcd, abd, abe, ac, empty],
        abc,
        set(abc),
        set_keys_consistent_symmetric,
    )
    assert right_processed == True
    assert processed == [(ab, abc), (abc, abc), (abce, abc), (abcd, abc), (ac, abc), (empty, abc)]
    assert skipped == [(abd, abc), (abe, abc)]
    assert skipped_left_keys == {abd, abe}
    assert processed_left_keys == {ab, abc, abce, abcd, ac, empty}
    assert skipped_right_keys == set()
    assert processed_right_keys == {abc}

    (
        right_processed,
        processed,
        skipped,
        skipped_left_keys,
        processed_left_keys,
        skipped_right_keys,
        processed_right_keys,
    ) = call_match(
        [ab, abc, abce, abcd, abd, abe, ac, empty],
        abc,
        set(abc),
        set_keys_consistent_left_in_right,
    )
    assert right_processed == True
    assert processed == [(ab, abc), (abc, abc), (ac, abc), (empty, abc)]
    assert skipped == [(abce, abc), (abcd, abc), (abd, abc), (abe, abc)]
    assert skipped_left_keys == {abd, abce, abcd, abe}
    assert processed_left_keys == {ab, abc, ac, empty}
    assert skipped_right_keys == set()
    assert processed_right_keys == {abc}

    (
        right_processed,
        processed,
        skipped,
        skipped_left_keys,
        processed_left_keys,
        skipped_right_keys,
        processed_right_keys,
    ) = call_match(
        [ab, abc, abce, abcd, abd, abe, ac, empty],
        abc,
        set(abc),
        set_keys_consistent_right_in_left,
    )
    assert right_processed == True
    assert processed == [(abc, abc), (abce, abc), (abcd, abc)]
    assert skipped == [(ab, abc), (abd, abc), (abe, abc), (ac, abc), (empty, abc)]
    assert skipped_left_keys == {ab, abd, abe, ac, empty}
    assert processed_left_keys == {abc, abce, abcd}
    assert skipped_right_keys == set()
    assert processed_right_keys == {abc}

    (
        right_processed,
        processed,
        skipped,
        skipped_left_keys,
        processed_left_keys,
        skipped_right_keys,
        processed_right_keys,
    ) = call_match(
        [ab, abc, abce, abcd, abd, abe, ac],
        x,
        set(x),
        set_keys_consistent_symmetric,
    )
    assert right_processed == False
    assert processed == []
    assert skipped == [(ab, x), (abc, x), (abce, x), (abcd, x), (abd, x), (abe, x), (ac, x)]
    assert skipped_left_keys == {ab, abc, abce, abcd, abd, abe, ac}
    assert processed_left_keys == set()
    assert skipped_right_keys == {x}
    assert processed_right_keys == set()

    with raises(ValueError):
        (
            right_processed,
            processed,
            skipped,
            skipped_left_keys,
            processed_left_keys,
            skipped_right_keys,
            processed_right_keys,
        ) = call_match(
            [ab, abc, abc, abce, abcd, abd, abe, ac, empty],
            abc,
            set(abc),
            set_keys_consistent_symmetric,
            require_no_duplicate_right_matches=True,
        )


def test_match_0():
    ab = tuple("ab")
    abc = tuple("abc")
    abce = tuple("abce")
    abcd = tuple("abcd")
    abd = tuple("abd")
    abe = tuple("abe")
    ac = tuple("ac")
    x = tuple("x")
    empty = tuple()

    def call_match(lefts, right, **kwargs):
        processed, skipped = [], []

        def fcn_take(i, left, right):
            processed.append((i, left, right))

        def fcn_reject(i, left, right):
            skipped.append((i, left, right))

        match_keys(lefts, right, fcn_take, fcn_on_reject=fcn_reject, **kwargs)

        return (processed, skipped)

    (
        processed,
        skipped,
    ) = call_match(
        [[ab, abc, abce, abcd, abd, abe, ac, empty]],
        [abc, abd],
        left_in_right=True,
        right_in_left=True,
        require_all_left_keys_processed=False,
    )
    assert processed == [
        (0, ab, abc),
        (0, abc, abc),
        (0, abce, abc),
        (0, abcd, abc),
        (0, ac, abc),
        (0, empty, abc),
        (0, ab, abd),
        (0, abcd, abd),
        (0, abd, abd),
        (0, empty, abd),
    ]
    assert skipped == [
        (0, abd, abc),
        (0, abe, abc),
        (0, abc, abd),
        (0, abce, abd),
        (0, abe, abd),
        (0, ac, abd),
    ]

    (
        processed,
        skipped,
    ) = call_match(
        [[ab, abc, abce, abcd], [abd, abe, ac, empty]],
        [abc, abd],
        left_in_right=True,
        right_in_left=True,
        require_all_left_keys_processed=False,
    )
    assert processed == [
        (0, ab, abc),
        (0, abc, abc),
        (0, abce, abc),
        (0, abcd, abc),
        (1, ac, abc),
        (1, empty, abc),
        (0, ab, abd),
        (0, abcd, abd),
        (1, abd, abd),
        (1, empty, abd),
    ]
    assert skipped == [
        (1, abd, abc),
        (1, abe, abc),
        (0, abc, abd),
        (0, abce, abd),
        (1, abe, abd),
        (1, ac, abd),
    ]


def test_match_1():
    a = tuple("a")
    b = tuple("b")
    a1 = tuple("a1")
    a2 = tuple("a2")
    b1 = tuple("b1")
    b2 = tuple("b2")
    ax = tuple("ax")
    ay = tuple("ay")
    bx = tuple("bx")
    by = tuple("by")
    a1x = tuple("a1x")
    a2x = tuple("a2x")
    b1x = tuple("b1x")
    b2x = tuple("b2x")
    a1y = tuple("a1y")
    a2y = tuple("a2y")
    b1y = tuple("b1y")
    b2y = tuple("b2y")
    empty = tuple()

    def call_match(lefts, right, **kwargs):
        processed, skipped = [], []

        def fcn_take(i, left, right):
            processed.append((i, left, right))

        def fcn_reject(i, left, right):
            skipped.append((i, left, right))

        match_keys(lefts, right, fcn_take, fcn_on_reject=fcn_reject, **kwargs)

        return (processed, skipped)

    (
        processed,
        skipped,
    ) = call_match(
        [[a, b], [a1, b1, a2, b2], [ax, bx, ay, by]],
        [a1x, a2x, b1x, b2x, a1y, a2y, b1y, b2y],
        left_in_right=True,
        right_in_left=False,
        require_all_left_keys_processed=True,
    )
    assert processed == [
        (0, a, a1x),
        (1, a1, a1x),
        (2, ax, a1x),
        (0, a, a2x),
        (1, a2, a2x),
        (2, ax, a2x),
        (0, b, b1x),
        (1, b1, b1x),
        (2, bx, b1x),
        (0, b, b2x),
        (1, b2, b2x),
        (2, bx, b2x),
        (0, a, a1y),
        (1, a1, a1y),
        (2, ay, a1y),
        (0, a, a2y),
        (1, a2, a2y),
        (2, ay, a2y),
        (0, b, b1y),
        (1, b1, b1y),
        (2, by, b1y),
        (0, b, b2y),
        (1, b2, b2y),
        (2, by, b2y),
    ]

    # Missing left a2 and b2
    with raises(ValueError):
        (
            processed,
            skipped,
        ) = call_match(
            [[a, b], [a1, b1], [ax, bx, ay, by]],
            [a1x, a2x, b1x, b2x, a1y, a2y, b1y, b2y],
            left_in_right=True,
            right_in_left=False,
            require_all_left_keys_processed=True,
            require_all_right_keys_processed=True,
            require_all_left_keys_match_right=True,
        )

    (
        processed,
        skipped,
    ) = call_match(
        [[a, b], [a1, b1], [ax, bx, ay, by]],
        [a1x, a2x, b1x, b2x, a1y, a2y, b1y, b2y],
        left_in_right=True,
        right_in_left=False,
        require_all_left_keys_processed=True,
        require_all_right_keys_processed=True,
        require_all_left_keys_match_right=False,
    )
    assert processed == [
        (0, a, a1x),
        (1, a1, a1x),
        (2, ax, a1x),
        (0, a, a2x),
        # (1, a2, a2x),
        (2, ax, a2x),
        (0, b, b1x),
        (1, b1, b1x),
        (2, bx, b1x),
        (0, b, b2x),
        # (1, b2, b2x),
        (2, bx, b2x),
        (0, a, a1y),
        (1, a1, a1y),
        (2, ay, a1y),
        (0, a, a2y),
        # (1, a2, a2y),
        (2, ay, a2y),
        (0, b, b1y),
        (1, b1, b1y),
        (2, by, b1y),
        (0, b, b2y),
        # (1, b2, b2y),
        (2, by, b2y),
    ]

    (
        processed,
        skipped,
    ) = call_match(
        [[a, b], [a1, b1], [ax, bx, ay, by]],
        [a1x, a2x, b1x, b2x, a1y, a2y, b1y, b2y],
        left_in_right=True,
        right_in_left=False,
        require_all_left_keys_processed=True,
        require_all_right_keys_processed=True,
        require_all_left_keys_match_right=False,
        unmatched_right_keys_should_contain=[("2",)]
    )
    assert processed == [
        (0, a, a1x),
        (1, a1, a1x),
        (2, ax, a1x),
        (0, a, a2x),
        # (1, a2, a2x),
        (2, ax, a2x),
        (0, b, b1x),
        (1, b1, b1x),
        (2, bx, b1x),
        (0, b, b2x),
        # (1, b2, b2x),
        (2, bx, b2x),
        (0, a, a1y),
        (1, a1, a1y),
        (2, ay, a1y),
        (0, a, a2y),
        # (1, a2, a2y),
        (2, ay, a2y),
        (0, b, b1y),
        (1, b1, b1y),
        (2, by, b1y),
        (0, b, b2y),
        # (1, b2, b2y),
        (2, by, b2y),
    ]

    with raises(ValueError):
        (
            processed,
            skipped,
        ) = call_match(
            [[a, b], [a1, b1], [ax, bx, ay, by]],
            [a1x, a2x, b1x, b2x, a1y, a2y, b1y, b2y],
            left_in_right=True,
            right_in_left=False,
            require_all_left_keys_processed=True,
            require_all_right_keys_processed=True,
            require_all_left_keys_match_right=False,
            unmatched_right_keys_should_contain=[("2", "a")]
        )
    (
        processed,
        skipped,
    ) = call_match(
        [[a, b], [a1, b1], [ax, bx, ay, by]],
        [a1x, a2x, b1x, b2x, a1y, a2y, b1y, b2y],
        left_in_right=True,
        right_in_left=False,
        require_all_left_keys_processed=True,
        require_all_right_keys_processed=True,
        require_all_left_keys_match_right=False,
        unmatched_right_keys_should_contain=[("2", "a"), ("b", "2")]
    )
    assert processed == [
        (0, a, a1x),
        (1, a1, a1x),
        (2, ax, a1x),
        (0, a, a2x),
        # (1, a2, a2x),
        (2, ax, a2x),
        (0, b, b1x),
        (1, b1, b1x),
        (2, bx, b1x),
        (0, b, b2x),
        # (1, b2, b2x),
        (2, bx, b2x),
        (0, a, a1y),
        (1, a1, a1y),
        (2, ay, a1y),
        (0, a, a2y),
        # (1, a2, a2y),
        (2, ay, a2y),
        (0, b, b1y),
        (1, b1, b1y),
        (2, by, b1y),
        (0, b, b2y),
        # (1, b2, b2y),
        (2, by, b2y),
    ]


def test_match_stub():
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
        require_all_left_keys_processed=False,
        require_all_right_keys_processed=False,
        fcn_on_reject=print_skip,
    )
    print()

    print("left, right extra")
    match_keys(
        (left,),
        right_extra,
        print,
        require_all_left_keys_processed=False,
        require_all_right_keys_processed=False,
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
