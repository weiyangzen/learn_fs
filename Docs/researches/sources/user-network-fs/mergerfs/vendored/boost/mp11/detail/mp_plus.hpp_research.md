<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_plus.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_plus.hpp

## Purpose

Implements `boost::mp11::mp_plus`, a header-only metafunction that sums the `::value` members of integral-constant types and returns a `std::integral_constant` whose value type follows C++ usual arithmetic conversions. It is a private-detail building block used by higher-level MP11 algorithms that need compile-time arithmetic.

## Important APIs, Types, and Functions

The public alias is `template<class... T> using mp_plus = typename detail::mp_plus_impl<T...>::type`. `detail::mp_plus_impl` has a fold-expression implementation when the compiler supports it and otherwise recursive specializations, including a ten-at-a-time path to reduce template depth. Detected alias templates include `mp_plus`. Implementation structs include `mp_plus_impl`.

## Control Flow

Instantiation selects the fold path or compatibility path from `detail/config.hpp`. The empty pack yields `std::integral_constant<int, 0>`. Non-empty packs accumulate `T::value`, preserving the computed expression type with `decltype` in modern compilers or by recursive addition in older compilers.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/detail/config.hpp`, `type_traits`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

All operands must expose a usable constant `value`; bad inputs fail at template substitution. Signed/unsigned mixing follows C++ conversion rules and can surprise callers. The fallback exists for old GCC/MSVC/Clang behavior, so changes must be tested with the supported compiler matrix.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_plus.hpp -->
