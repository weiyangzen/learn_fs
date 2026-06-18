<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/list.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/list.hpp

## Purpose

Defines MP11 list manipulation primitives for type lists and, where supported, value lists. It is the main public header for list size, rebinding, element access, push/pop, replacement, and element transformation.

## Important APIs, Types, and Functions

Exports `mp_list_c`, `mp_size`, `mp_empty`, `mp_assign`, `mp_clear`, `mp_pop_front`, `mp_first`, `mp_rest`, `mp_second`, `mp_third`, `mp_push_front`, `mp_push_back`, `mp_rename_v`, `mp_replace_front/first/second/third`, and `mp_transform_front/first/second/third` plus `_q` quoted variants. Detected alias templates include `mp_list_c`, `mp_size`, `mp_empty`, `mp_assign`, `mp_clear`, `mp_pop_front`, `mp_first`, `mp_rest`, `mp_second`, `mp_third`, `mp_push_front`, `mp_push_back`, `mp_rename_v`, `mp_replace_front`, `mp_replace_first`, `mp_replace_second`, `mp_replace_third`, `mp_transform_front`. Implementation structs include `mp_size_impl`, `mp_assign_impl`, `mp_pop_front_impl`, `mp_second_impl`, `mp_third_impl`, `mp_push_front_impl`, `mp_push_back_impl`, `mp_rename_v_impl`, `mp_replace_front_impl`, `mp_replace_second_impl`.

## Control Flow

Most operations partially specialize on `L<T...>` and rebuild the same outer template with modified element packs. Template-auto branches support `L<A...>` value lists by converting between raw values and `mp_value` wrappers. Diagnostics are intentionally expressed as missing `type` when an input is not a list or is too short.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integral.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_list_v.hpp`, `boost/mp11/detail/mp_is_list.hpp`, `boost/mp11/detail/mp_is_value_list.hpp`, `boost/mp11/detail/mp_front.hpp`, `boost/mp11/detail/mp_rename.hpp`, `boost/mp11/detail/mp_append.hpp`, `boost/mp11/detail/config.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

Operations preserve the original outer template, which is useful but can surprise when the target container has constraints. Empty or too-short lists fail at compile time. The temporary push/pop of macro `I` protects against platform headers that define `I` as a macro.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/list.hpp -->
