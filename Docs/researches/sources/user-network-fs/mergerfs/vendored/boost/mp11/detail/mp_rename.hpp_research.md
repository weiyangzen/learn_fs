<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_rename.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_rename.hpp

## Purpose

Provides list-template rebinding and application helpers: `mp_rename`, `mp_apply`, and `mp_apply_q`. These are central MP11 adapters for turning one variadic type-list representation into another or invoking a metafunction over list elements.

## Important APIs, Types, and Functions

`mp_rename<L, B>` rebuilds `L<T...>` as `B<T...>`. `mp_apply<F, L>` applies template `F` to list elements. `mp_apply_q<Q, L>` invokes quoted metafunction `Q::template fn`. When template-auto is enabled it also supports value-list templates by wrapping auto arguments with `mp_value` when applying type metafunctions. Detected alias templates include `mp_rename`, `mp_apply`, `mp_apply_q`. Implementation structs include `mp_rename_impl`.

## Control Flow

Specializations unpack either `template<class...>` or `template<auto...>` lists, then recompose the destination template. `mp_defer` is included to delay invalid applications until selected, which supports SFINAE-friendly higher-level utilities.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/detail/mp_defer.hpp`, `boost/mp11/detail/mp_value.hpp`, `boost/mp11/detail/config.hpp`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

Input must be a recognized variadic list shape. Value-list support depends on compiler feature macros. Applying a metafunction that rejects the element pack gives compile-time diagnostics at the alias instantiation site.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_rename.hpp -->
