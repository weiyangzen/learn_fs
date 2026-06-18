# sources/storage-engines/foundationdb/bindings/c/test/mako/macro.hpp

## Purpose
Defines a compiler-specific `force_inline` macro for Mako hot-path helpers.

## Important APIs, types, and functions
`force_inline` maps to GNU `inline __attribute__((__always_inline__))` or MSVC `__forceinline`.

## Control flow
Compile-time preprocessor branching selects the implementation.

## State and persistence behavior
No runtime state or persistence.

## Dependencies and integration points
Included by Mako headers such as `future.hpp` for aggressive inlining.

## Risks and test signals
Unsupported compilers fail with `#error Missing force inline`; excessive inlining can affect code size/debuggability.
