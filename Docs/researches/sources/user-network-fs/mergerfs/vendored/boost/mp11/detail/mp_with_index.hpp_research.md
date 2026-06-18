<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_with_index.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_with_index.hpp

## Purpose

Implements `mp_with_index`, a runtime-to-compile-time bridge that calls a function object with an `mp_size_t<I>` corresponding to a runtime index. It supports efficient dispatch over bounded index ranges.

## Important APIs, Types, and Functions

`mp_with_index<N>(i, f)` asserts `i < N` and invokes `f(mp_size_t<I>{})`. Internals provide `detail::mp_with_index_impl<N>::call`, specialized switch tables for many power-of-two and small fixed sizes, plus constexpr/unreachable macros for compiler optimization. Implementation structs include `mp_with_index_impl_`.

## Control Flow

The runtime index is checked, then dispatch enters a generated switch or recursive range split. Each case materializes the chosen index as a type, allowing downstream code to select tuple elements, array slots, or type-list positions at compile time while still receiving the index from runtime input.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/integral.hpp`, `boost/mp11/detail/config.hpp`, `type_traits`, `utility`, `cassert`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

The assertion is the only runtime guard in release builds if assertions are disabled, so callers must respect `i < N`. Large `N` expands substantial switch/template code. Return-type consistency is required across all possible `f(mp_size_t<I>)` calls.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_with_index.hpp -->
