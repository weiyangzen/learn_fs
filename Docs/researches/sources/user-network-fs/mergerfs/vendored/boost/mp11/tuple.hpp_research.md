<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/tuple.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/tuple.hpp

## Purpose

Adds runtime tuple algorithms that use MP11 integer sequences: apply a callable to tuple elements, construct an object from a tuple, iterate a tuple, and transform one or more tuple-like objects element-wise.

## Important APIs, Types, and Functions

Exports `tuple_apply`, `construct_from_tuple`, `tuple_for_each`, and `tuple_transform`. It uses unqualified `get` via `using std::get` so tuple-like types can participate through ADL, and derives index ranges from `std::tuple_size`.

## Control Flow

Each algorithm builds a `make_index_sequence` for the tuple length. `tuple_apply` expands `get<J>(tp)...` into the callable. `construct_from_tuple` forwards elements into `T(...)`. `tuple_for_each` uses an initializer-list expansion for ordered side effects. `tuple_transform` groups same-index elements across all input tuples and returns a new `std::tuple` of results.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integer_sequence.hpp`, `boost/mp11/list.hpp`, `boost/mp11/function.hpp`, `boost/mp11/detail/config.hpp`, `tuple`, `utility`, `type_traits`, `cstddef`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

All tuple inputs to `tuple_transform` must have the same length. Result/value categories are encoded through forwarding helper tuples, so dangling references are possible if callers store tuples of references beyond source lifetimes. Old MSVC branches limit variadic transform behavior.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/tuple.hpp -->
