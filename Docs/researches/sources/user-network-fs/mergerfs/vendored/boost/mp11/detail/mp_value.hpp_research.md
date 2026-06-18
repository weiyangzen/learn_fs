<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_value.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_value.hpp

## Purpose

Defines `mp_value`, the MP11 wrapper for non-type template values. It makes `auto` template parameters usable in type-list algorithms by presenting a `std::integral_constant`-like type.

## Important APIs, Types, and Functions

With template-auto support, `template<auto A> using mp_value = std::integral_constant<decltype(A), A>`. On older compilers, the fallback is a small struct template `mp_value<T, A>` inheriting from `std::integral_constant<T, A>`. Detected alias templates include `mp_value`.

## Control Flow

The header is selected by `BOOST_MP11_HAS_TEMPLATE_AUTO`. Higher-level list/value-list adapters use `mp_value<A>` to convert raw non-type arguments into types with `::value` and `value_type`.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/detail/config.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

The public spelling differs across compiler feature sets, so code should consume it through MP11 aliases rather than depending on implementation details. Values must be legal non-type template arguments for the active language mode.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_value.hpp -->
