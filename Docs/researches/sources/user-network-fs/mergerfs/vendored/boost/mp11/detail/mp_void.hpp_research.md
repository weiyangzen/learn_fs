<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_void.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_void.hpp

## Purpose

Implements `mp_void`, MP11’s equivalent of `void_t`, for SFINAE probes and lazy validity checks.

## Important APIs, Types, and Functions

Modern compilers get `template<class...> using mp_void = void`; old MSVC uses `detail::mp_void_impl<T...>::type` to avoid alias-template substitution bugs. Detected alias templates include `mp_void`. Implementation structs include `mp_void_impl`.

## Control Flow

Callers instantiate `mp_void<Expr...>` in a default template parameter or partial specialization. If all expressions are well-formed the result is `void`; otherwise substitution fails and another overload/specialization can be chosen.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are none. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

It is intentionally minimal. Behavior depends on substitution context; outside SFINAE a bad expression is still a hard compile error. The compatibility branch should not be simplified without old-compiler coverage.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/detail/mp_void.hpp -->
