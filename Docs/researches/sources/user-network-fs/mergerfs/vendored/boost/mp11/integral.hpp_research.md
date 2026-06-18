<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/integral.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/integral.hpp

## Purpose

Defines common MP11 integral constants and boolean adapters used throughout the library.

## Important APIs, Types, and Functions

Exports `mp_bool<B>`, `mp_true`, `mp_false`, `mp_to_bool<T>`, `mp_not<T>`, `mp_int<I>`, `mp_size_t<N>`, and includes `mp_value` for non-type value wrappers. Detected alias templates include `mp_bool`, `mp_to_bool`, `mp_not`, `mp_int`, `mp_size_t`.

## Control Flow

The aliases map directly to `std::integral_constant` forms. Higher-level metafunctions use these stable names instead of repeating standard-library spellings and to normalize arbitrary `T::value` constants to bool.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/version.hpp`, `boost/mp11/detail/mp_value.hpp`, `type_traits`, `cstddef`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

This header has no runtime behavior, but all consumers assume `::value` exists and is constant-expression friendly. Compile errors here usually indicate a non-integral-constant input passed into MP11 logic.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/integral.hpp -->
