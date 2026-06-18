# sources/sync-backup/casync/src/gcc-macro.h

## Purpose

`gcc-macro.h` centralizes compiler attribute and branch prediction macros used across the C codebase.

## Important APIs, Types, and Functions

It defines `_printf_`, `_sentinel_`, `_unused_`, `_likely_`, `_unlikely_`, `_malloc_`, `_pure_`, `_packed_`, `_const_`, `_alloc_`, and `_fallthrough_`. `_alloc_` expands to `alloc_size` on GCC and empty on clang. `_fallthrough_` is enabled for GCC 7+ and empty otherwise.

## Control Flow

There is no runtime control flow. `_likely_` and `_unlikely_` influence compiler branch prediction. `_fallthrough_` annotates intentional switch fall-through.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

This header is consumed by `util.h` and many source files that use attributes such as `_packed_` for on-disk formats or `_pure_` for helper declarations.

## Risks and Edge Cases

`_unused_` is defined twice identically. Attribute support is compiler-specific; clang gets an empty `_alloc_`. The macros are unnamespaced except for underscores and could conflict if included alongside other portability layers.

## Test Signals

Build tests with GCC and clang should verify no warnings/errors for attributes, switch fall-through annotations, packed structs, and format-string checking.
