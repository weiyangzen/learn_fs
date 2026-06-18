<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/integer_sequence.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/mp11/integer_sequence.hpp

## Purpose

Provides MP11’s C++11-compatible implementation of `integer_sequence`, `index_sequence`, and sequence-generation aliases, with compiler-intrinsic fast paths when available.

## Important APIs, Types, and Functions

Defines `integer_sequence<T, I...>`, `make_integer_sequence<T, N>`, `index_sequence`, `make_index_sequence<N>`, and `index_sequence_for<T...>`. It can use `__make_integer_seq` where available, otherwise builds sequences by recursive splitting and append. Detected alias templates include `make_integer_sequence`, `iseq_if_c`, `make_integer_sequence`, `index_sequence`, `make_index_sequence`, `index_sequence_for`. Implementation structs include `integer_sequence`, `iseq_if_c_impl`, `iseq_identity`, `append_integer_sequence`, `make_integer_sequence_impl`, `make_integer_sequence_impl_`.

## Control Flow

For generated sequences the fallback recursively halves `N`, creates smaller sequences, appends them with shifted values, and conditionally adds the final odd element. Negative `N` resolves to a missing type through `iseq_if_c`, producing a compile-time error.

## State and Persistence Behavior

This header is compile-time only. It defines templates, aliases, or macros and stores no runtime state, global mutable data, file handles, or persistent data. State exists only as compiler instantiation state and, for tuple utilities, as caller-owned values forwarded through inline functions.

## Dependencies and Integration Points

Direct includes are `boost/mp11/version.hpp`, `cstddef`. The header integrates with the rest of vendored Boost.MP11 under `boost::mp11`; mergerfs receives it as vendored header-only infrastructure for template metaprogramming without a system Boost requirement.

## Risks and Edge Cases

Large sequence generation can be template-heavy without compiler intrinsics. `N` must be non-negative and fit the selected integral type. The implementation is low-level infrastructure for tuple/list algorithms, so off-by-one errors would cascade broadly.

## Test Signals

Useful signals are compile-only tests that instantiate the documented aliases/functions with normal, empty, boundary, and invalid inputs; mergerfs build jobs that include vendored Boost headers; and, where compiler workarounds are present, CI coverage on GCC, Clang, and MSVC-like modes matching the guarded branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/mp11/integer_sequence.hpp -->
