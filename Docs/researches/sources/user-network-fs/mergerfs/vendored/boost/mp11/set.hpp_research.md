<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/set.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/set.hpp

## Purpose

Implements set-like algorithms over MP11 type lists, treating type identity as membership and preserving list order where possible.

## Important APIs, Types, and Functions

Exports `mp_set_contains`, `mp_set_push_back`, `mp_set_push_front`, `mp_is_set`, `mp_set_union`, `mp_set_intersection`, and `mp_set_difference`. It uses `mp_inherit<mp_identity<T>...>` for efficient membership, plus fold/copy/remove helpers. Detected alias templates include `mp_set_contains`, `mp_set_push_back`, `mp_set_push_front`, `mp_is_set`, `mp_set_union_`, `mp_set_union`, `mp_set_intersection_`, `mp_set_intersection`, `mp_set_difference`. Implementation structs include `mp_set_contains_impl`, `mp_set_push_back_impl`, `mp_set_push_front_impl`, `mp_is_set_helper_start`, `mp_is_set_helper`, `mp_is_set_impl`, `mp_set_union_impl`, `in_all_sets`, `mp_set_intersection_impl`, `in_any_set`.

## Control Flow

Membership is tested through base-class lookup. Push operations add only absent types. `mp_is_set` folds through the pack to detect duplicates. Union appends missing elements from later lists; intersection copies elements present in all other sets; difference removes elements present in any excluded set.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/utility.hpp`, `boost/mp11/function.hpp`, `boost/mp11/detail/config.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_append.hpp`, `boost/mp11/detail/mp_copy_if.hpp`, `boost/mp11/detail/mp_fold.hpp`, `boost/mp11/detail/mp_remove_if.hpp`, `boost/mp11/detail/mp_is_list.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

These are type-identity sets, not value or trait equivalence sets. Duplicate handling is deterministic but template-heavy on very large packs. Non-list operands trigger substitution failures through `mp_is_list` gates or missing implementation `type`s.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/set.hpp -->
