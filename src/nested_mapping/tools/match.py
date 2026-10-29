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


def match_keys_to_set_key(
    keys_left: Sequence[KeyLike],
    key_right_proper: TupleKey,
    set_key_right: set,
    keys_consistent: Callable[[set | OrderedSet, set | OrderedSet], bool],
    fcn: Callable[[TupleKey, TupleKey], Any],
    *,
    fcn_on_skip: Callable[[TupleKey, TupleKey], Any] | None = None,
    require_all_left_keys_match_right: bool,
    collect_skipped_left_keys: bool,
    skipped_left_keys_in_total: set,
    processed_left_keys_in_total: set,
    processed_right_keys_i: set,
    skipped_right_keys_i: set,
) -> bool:
    right_processed = False
    for key_left in keys_left:
        key_left_proper = properkey(key_left)
        set_key_left = OrderedSet(key_left_proper)
        if not keys_consistent(set_key_left, set_key_right):
            if collect_skipped_left_keys:
                if key_left_proper not in processed_left_keys_in_total:
                    skipped_left_keys_in_total.add(key_left_proper)
            if require_all_left_keys_match_right:
                if key_right_proper not in processed_right_keys_i:
                    skipped_right_keys_i.add(key_right_proper)
            if fcn_on_skip:
                fcn_on_skip(key_left_proper, key_right_proper)
            continue

        fcn(key_left_proper, key_right_proper)
        right_processed = True

        if collect_skipped_left_keys:
            with suppress(KeyError):
                skipped_left_keys_in_total.remove(key_left_proper)
            processed_left_keys_in_total.add(key_left_proper)

        if require_all_left_keys_match_right:
            with suppress(KeyError):
                skipped_right_keys_i.remove(key_right_proper)
            processed_right_keys_i.add(key_right_proper)

    return right_processed

def zip_match_keys_to_set_key(
    keys_left: Sequence[KeyLike],
    tuple_key_right: TupleKey,
    set_key_right: set,
    keys_consistent_fcn: Callable[[set | OrderedSet, set | OrderedSet], bool],
):
    for key_left in keys_left:
        tuple_key_left = properkey(key_left)
        set_key_left = OrderedSet(tuple_key_left)
        if keys_consistent_fcn(set_key_left, set_key_right):
            yield tuple_key_left, tuple_key_right

def match_keys(
    keys_left_seq: Sequence[Sequence[KeyLike]],
    keys_right: Iterable[KeyLike],
    fcn: Callable[[int, TupleKey, TupleKey], Any],
    *,
    fcn_outer_before: Callable[[TupleKey], Any] | None = None,
    fcn_outer_after: Callable[[TupleKey], Any] | None = None,
    fcn_on_skip: Callable[[int, TupleKey, TupleKey], Any] | None = None,
    left_in_right: bool = True,
    right_in_left: bool = True,
    require_all_right_keys_processed: bool = True,
    require_all_left_keys_processed: bool = True,
    require_all_left_keys_match_right: bool = True,
    skippable_left_keys_should_contain: Sequence[KeyLike] | None = None,
) -> None:
    if isinstance(keys_right, str):
        raise RuntimeError("`keys_right` should be iterable, but not string")
    if not keys_left_seq:
        raise RuntimeError("Left sequence is empty")

    if left_in_right and right_in_left:
        keys_consistent = set_keys_consistent_symmetric
    elif left_in_right:
        keys_consistent = set_keys_consistent_left_in_right
    elif right_in_left:
        keys_consistent = set_keys_consistent_right_in_left

    else:
        raise RuntimeError(
            "At least on of the flags should be true: right_in_left or left_in_right"
        )

    skipped_right_keys = []
    processed_right_keys = set()
    processed_left_keys_in_total = set()
    skipped_left_keys_in_total = set()
    skipped_right_keys_for_left = []
    processed_right_keys_for_left = []

    collect_skipped_left_keys = (
        require_all_left_keys_processed or skippable_left_keys_should_contain
    )

    i_left = -1
    for key_right in keys_right:
        key_right_proper = properkey(key_right)
        setkey_right = OrderedSet(key_right_proper)
        if fcn_outer_before is not None:
            fcn_outer_before(key_right_proper)

        right_processed = False
        for i_left, keys_left in enumerate(keys_left_seq):
            if i_left >= len(skipped_right_keys_for_left):
                processed_right_keys_for_left.append(processed_right_keys_i := set())
                skipped_right_keys_for_left.append(skipped_right_keys_i := set())
            else:
                processed_right_keys_i = processed_right_keys_for_left[i_left]
                skipped_right_keys_i = skipped_right_keys_for_left[i_left]

            for key_left in keys_left:
                if key_left:
                    key_left_proper = properkey(key_left)
                    setkey_left = OrderedSet(key_left_proper)
                    if not keys_consistent(setkey_left, setkey_right):
                        if collect_skipped_left_keys:
                            if key_left_proper not in processed_left_keys_in_total:
                                skipped_left_keys_in_total.add(key_left_proper)
                        if require_all_left_keys_match_right:
                            if key_right_proper not in processed_right_keys_i:
                                skipped_right_keys_i.add(key_right_proper)
                        if fcn_on_skip:
                            fcn_on_skip(i_left, key_left_proper, key_right_proper)
                        continue
                else:
                    key_left_proper = ()

                fcn(i_left, key_left_proper, key_right_proper)
                right_processed = True

                if collect_skipped_left_keys:
                    with suppress(KeyError):
                        skipped_left_keys_in_total.remove(key_left_proper)
                    processed_left_keys_in_total.add(key_left_proper)

                if require_all_left_keys_match_right:
                    with suppress(KeyError):
                        skipped_right_keys_i.remove(key_right_proper)
                    processed_right_keys_i.add(key_right_proper)

        if fcn_outer_after is not None:
            fcn_outer_after(key_right_proper)

        if right_processed:
            if require_all_left_keys_match_right:
                processed_right_keys.add(key_right_proper)
        elif require_all_right_keys_processed:
            skipped_right_keys.append(key_right_proper)

    if require_all_left_keys_match_right:
        for i, (skipped_left_keys_i, processed_left_keys_i) in enumerate(
            zip(skipped_right_keys_for_left, processed_right_keys_for_left)
        ):
            if processed_left_keys_i != processed_right_keys:
                raise ValueError(
                    f"match_keys: left sequence {i} did not provide keys {skipped_left_keys_i!s}"
                )

    if skipped_left_keys_in_total:
        if require_all_left_keys_processed:
            raise ValueError(
                f"match_keys: there were unprocessed left keys {skipped_left_keys_in_total!s}"
            )
        failure, incorrectly_skipped_key = _check_skipped_keys_incorrect(
            skipped_left_keys_in_total, skippable_left_keys_should_contain
        )
        if failure:
            raise ValueError(
                f"match_keys: there were unprocessed left keys {skipped_left_keys_in_total!s}. "
                f"{incorrectly_skipped_key} should not have been skipped."
            )

    if require_all_right_keys_processed and skipped_right_keys:
        raise ValueError(f"match_keys: there were unprocessed right keys {skipped_right_keys!s}")


def _check_skipped_keys_incorrect(
    skipped_keys: Sequence[Key] | set[Key], should_contain: Sequence[KeyLike] | None
) -> tuple[bool, Key | None]:
    if not should_contain:
        return False, None

    setkeys = tuple(setkey(keypart) for keypart in should_contain)
    for skipped_key in skipped_keys:
        if not any(setkey.issubset(skipped_key) for setkey in setkeys):
            return True, skipped_key

    return False, None
