<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/version.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/version.hpp

## Purpose

Declares the vendored Boost.MP11 version macro.

## Important APIs, Types, and Functions

Defines `BOOST_MP11_VERSION` as `109000`, representing the MP11 version encoded as a single integer.

## Control Flow

Including the header simply makes the macro available to conditional code and to other MP11 headers such as `integer_sequence.hpp` and `integral.hpp`.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are none. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

There is no runtime behavior. The risk is version skew if vendored headers are updated incompletely while this macro remains stale.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/version.hpp -->
