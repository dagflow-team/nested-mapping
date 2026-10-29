from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any

from ordered_set import OrderedSet

from ..typing import Key, KeyLike, TupleKey, properkey, setkey

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence


def set_keys_consistent_symmetric(
    set_key_left: set | OrderedSet, set_key_right: set | OrderedSet
) -> bool:
    return set_key_left.issubset(set_key_right) or set_key_right.issubset(set_key_left)


def set_keys_consistent_left_in_right(
    set_key_left: set | OrderedSet, set_key_right: set | OrderedSet
) -> bool:
    return set_key_left.issubset(set_key_right)


def set_keys_consistent_right_in_left(
    set_key_left: set | OrderedSet, set_key_right: set | OrderedSet
) -> bool:
    return set_key_right.issubset(set_key_left)


def match_keys_to_key(
    keys_left: Sequence[KeyLike],
    key_right_tuple: TupleKey,
    key_right_set: set | OrderedSet,
    keys_consistent: Callable[[set | OrderedSet, set | OrderedSet], bool],
    fcn: Callable[[TupleKey, TupleKey], Any],
    *,
    fcn_on_reject: Callable[[TupleKey, TupleKey], Any] | None = None,
    collect_skipped_right_keys: bool = False,
    collect_skipped_left_keys: bool = False,
    skipped_left_keys: set | None = None,
    processed_left_keys: set | None = None,
    processed_right_keys: set | None = None,
    skipped_right_keys: set | None = None,
    require_no_duplicate_right_matches: bool = False,
) -> bool:
    assert not collect_skipped_right_keys or (
        processed_right_keys is not None and skipped_right_keys is not None
    )
    assert not collect_skipped_left_keys or (
        processed_left_keys is not None and skipped_left_keys is not None
    )
    right_key_processed = False
    key_left_match = None
    for key_left in keys_left:
        key_left_tuple = properkey(key_left)
        key_left_set = OrderedSet(key_left_tuple)

        if not keys_consistent(key_left_set, key_right_set):
            if (
                collect_skipped_left_keys
                and key_left_tuple
                not in processed_left_keys  # pyright: ignore [reportOperatorIssue]
            ):
                skipped_left_keys.add(  # pyright: ignore [reportOptionalMemberAccess]
                    key_left_tuple
                )
            if (
                collect_skipped_right_keys
                and key_right_tuple
                not in processed_right_keys  # pyright: ignore [reportOperatorIssue]
            ):
                skipped_right_keys.add(  # pyright: ignore [reportOptionalMemberAccess]
                    key_right_tuple
                )
            if fcn_on_reject:
                fcn_on_reject(key_left_tuple, key_right_tuple)
            continue

        fcn(key_left_tuple, key_right_tuple)
        if require_no_duplicate_right_matches and right_key_processed:
            raise ValueError(
                f"match_keys: right key {key_right_tuple!s} was matched more than once to "
                f"{key_left_match!s}; {key_left_tuple!s}..."
            )

        right_key_processed = True
        key_left_match = key_left_tuple

        if collect_skipped_left_keys:
            with suppress(KeyError):
                skipped_left_keys.remove(
                    key_left_tuple
                )  # pyright: ignore [reportOptionalMemberAccess]
            processed_left_keys.add(key_left_tuple)  # pyright: ignore [reportOptionalMemberAccess]

        if collect_skipped_right_keys:
            with suppress(KeyError):
                skipped_right_keys.remove(
                    key_right_tuple
                )  # pyright: ignore [reportOptionalMemberAccess]
            processed_right_keys.add(key_right_tuple)  # pyright: ignore [reportOptionalMemberAccess]

    return right_key_processed


def zip_match_keys_to_key(
    keys_left: Sequence[KeyLike],
    key_right_tuple: TupleKey,
    key_right_set: set | OrderedSet,
    keys_consistent_fcn: Callable[[set | OrderedSet, set | OrderedSet], bool],
):
    for key_left in keys_left:
        key_left_tuple = properkey(key_left)
        key_left_set = OrderedSet(key_left_tuple)
        if keys_consistent_fcn(key_left_set, key_right_set):
            yield key_left_tuple, key_right_tuple


def zip_match_keys_to_keys(
    keys_left: Sequence[KeyLike],
    keys_right: Sequence[KeyLike],
    keys_consistent_fcn: Callable[[set | OrderedSet, set | OrderedSet], bool],
):
    for key_right in keys_right:
        key_right_tuple = properkey(key_right)
        key_right_set = OrderedSet(key_right_tuple)

        yield from zip_match_keys_to_key(
            keys_left, key_right_tuple, key_right_set, keys_consistent_fcn
        )


def match_keys(
    keys_left_seq: Sequence[Sequence[KeyLike]],
    keys_right: Iterable[KeyLike],
    fcn: Callable[[int, TupleKey, TupleKey], Any],
    *,
    fcn_outer_before: Callable[[TupleKey], Any] | None = None,
    fcn_outer_after: Callable[[TupleKey], Any] | None = None,
    fcn_on_reject: Callable[[int, TupleKey, TupleKey], Any] | None = None,
    left_in_right: bool = True,
    right_in_left: bool = True,
    require_all_right_keys_processed: bool = True,
    require_all_left_keys_processed: bool = True,
    require_all_left_keys_match_right: bool = True,
    require_no_duplicate_right_matches: bool = False,
    unmatched_right_keys_should_contain: Sequence[KeyLike] | None = None,
    skippable_left_keys_should_contain: Sequence[KeyLike] | None = None,
) -> None:
    if isinstance(keys_right, str):
        raise RuntimeError("`keys_right` should be iterable, but not string")
    if not keys_left_seq:
        raise RuntimeError("Left sequence is empty")

    if left_in_right and right_in_left:
        keys_consistent_fcn = set_keys_consistent_symmetric
    elif left_in_right:
        keys_consistent_fcn = set_keys_consistent_left_in_right
    elif right_in_left:
        keys_consistent_fcn = set_keys_consistent_right_in_left
    else:
        raise RuntimeError(
            "At least on of the flags should be true: right_in_left or left_in_right"
        )

    skipped_right_keys = []
    processed_right_keys = set()
    processed_left_keys = set()
    skipped_left_keys = set()
    skipped_right_keys_for_left = []
    processed_right_keys_for_left = []

    collect_skipped_left_keys = bool(
        require_all_left_keys_processed or skippable_left_keys_should_contain is not None
    )
    collect_skipped_right_keys = bool(
        require_all_left_keys_match_right or unmatched_right_keys_should_contain is not None
    )

    i_left = -1
    for key_right in keys_right:
        key_right_tuple = properkey(key_right)
        key_right_set = OrderedSet(key_right_tuple)
        if fcn_outer_before is not None:
            fcn_outer_before(key_right_tuple)

        right_key_processed = False
        for i_left, keys_left in enumerate(keys_left_seq):
            if i_left >= len(skipped_right_keys_for_left):
                processed_right_keys_for_left.append(processed_right_keys_i := set())
                skipped_right_keys_for_left.append(skipped_right_keys_i := set())
            else:
                processed_right_keys_i = processed_right_keys_for_left[i_left]
                skipped_right_keys_i = skipped_right_keys_for_left[i_left]

            right_key_processed = match_keys_to_key(
                keys_left,
                key_right_tuple,
                key_right_set,
                keys_consistent_fcn,
                lambda *args: fcn(i_left, *args),
                fcn_on_reject=(
                    (lambda *args: fcn_on_reject(i_left, *args))
                    if fcn_on_reject is not None
                    else None
                ),
                collect_skipped_left_keys=collect_skipped_left_keys,
                collect_skipped_right_keys=collect_skipped_right_keys,
                skipped_left_keys=skipped_left_keys,
                processed_left_keys=processed_left_keys,
                skipped_right_keys=skipped_right_keys_i,
                processed_right_keys=processed_right_keys_i,
                require_no_duplicate_right_matches=require_no_duplicate_right_matches,
            )

        if fcn_outer_after is not None:
            fcn_outer_after(key_right_tuple)

        if right_key_processed:
            if require_all_left_keys_match_right:
                processed_right_keys.add(key_right_tuple)
        elif require_all_right_keys_processed:
            skipped_right_keys.append(key_right_tuple)

    for i, (skipped_left_keys_i, processed_left_keys_i) in enumerate(
        zip(skipped_right_keys_for_left, processed_right_keys_for_left)
    ):
        if processed_left_keys_i != processed_right_keys:
            if require_all_left_keys_match_right:
                raise ValueError(
                    f"match_keys: left sequence {i} did not provide keys {skipped_left_keys_i!s}"
                )
            _check_for_unexpectedly_skipped_keys(
                skipped_left_keys_i,
                unmatched_right_keys_should_contain,
                kind=f"missing left ({i})",
            )

    if skipped_left_keys:
        if require_all_left_keys_processed:
            raise ValueError(f"match_keys: there were unprocessed left keys {skipped_left_keys!s}")
        _check_for_unexpectedly_skipped_keys(
            skipped_left_keys, unmatched_right_keys_should_contain, kind="skipped left"
        )

    if require_all_right_keys_processed and skipped_right_keys:
        raise ValueError(f"match_keys: there were unprocessed right keys {skipped_right_keys!s}")


def _check_for_unexpectedly_skipped_keys(
    skipped_keys: Sequence[Key] | set[Key], should_contain: Sequence[KeyLike] | None, kind: str
):
    if unexpectedly_skipped_keys := _get_unexpectedly_skipped_keys(skipped_keys, should_contain):
        raise ValueError(
            f"match_keys: there were {kind} keys {skipped_keys!s}. "
            f"{unexpectedly_skipped_keys} should not have been skipped."
        )


def _get_unexpectedly_skipped_keys(
    skipped_keys: Sequence[Key] | set[Key], should_contain: Sequence[KeyLike] | None
) -> Sequence[Key]:
    if not should_contain:
        return []

    setkeys = tuple(setkey(keypart) for keypart in should_contain)
    incorrectly_skipped_keys = []
    for skipped_key in skipped_keys:
        if not any(setkey.issubset(skipped_key) for setkey in setkeys):
            incorrectly_skipped_keys.append(skipped_key)

    return incorrectly_skipped_keys
