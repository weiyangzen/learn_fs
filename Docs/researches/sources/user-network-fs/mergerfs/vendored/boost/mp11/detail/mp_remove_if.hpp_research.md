<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_remove_if.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_remove_if.hpp

## Purpose

Defines `mp_remove_if` and `mp_remove_if_q`, list filters that remove elements for which a predicate is true. It is a detail header used by set/list algorithms while preserving the input list template.

## Important APIs, Types, and Functions

`mp_remove_if<L, P>` accepts a template predicate and `mp_remove_if_q<L, Q>` accepts a quoted predicate with `Q::template fn`. Internally `_f` maps each element to either an empty `mp_list<>` or singleton `mp_list<T>`, and `mp_append` flattens the kept elements. Detected alias templates include `mp_remove_if`, `mp_remove_if_q`. Implementation structs include `mp_remove_if_impl`, `_f`.

## Control Flow

The implementation specializes only list-like `L<T...>` forms. It transforms each element through `mp_eval_if<P<T>, mp_list<>, mp_list, T>` and appends the resulting small lists back into the original list shape.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/utility.hpp`, `boost/mp11/detail/mp_list.hpp`, `boost/mp11/detail/mp_append.hpp`, `boost/mp11/detail/config.hpp`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

The predicate must be valid for every element and expose a boolean `::value`. Non-list inputs intentionally produce a missing `type` diagnostic. Since this is type-level filtering, very large packs may still stress template instantiation limits.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_remove_if.hpp -->
