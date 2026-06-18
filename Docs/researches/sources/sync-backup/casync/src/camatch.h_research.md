# sources/sync-backup/casync/src/camatch.h

## Purpose
`camatch.h` declares the match-rule tree used by casync traversal code to include or exclude files and directories. It exposes the `CaMatch` structure, node type enum, lifecycle functions, tree mutation helpers, normalization, matching, dumping, and equality checks.

## Important APIs, Types, and Functions
`CaMatchType` has `CA_MATCH_POSITIVE`, `CA_MATCH_NEGATIVE`, and `CA_MATCH_INNER`. `struct CaMatch` contains a reference count, type, `anchored` and `directory_only` bitfields, a dynamically allocated child pointer array, allocation counters, and an inline `name[]`. Public constructors are `ca_match_new_from_file()` and `ca_match_new_from_strings()`. Public operations are `ca_match_ref()`, `ca_match_unref()`, `ca_match_add_child()`, `ca_match_merge()`, `ca_match_normalize()`, `ca_match_test()`, `ca_match_dump()`, and `ca_match_equal()`.

## Control Flow
The header reflects a tree API where callers build or parse a root, normalize it, then repeatedly call `ca_match_test()` while walking directories. If the caller supplies `ret` to `ca_match_test()`, the callee returns a new subtree representing rules to apply below a matched directory.

## State and Persistence
`CaMatch` objects are heap allocated and reference counted. Children are strong references. The structure deliberately exposes internals, which tests and nearby code use directly, but modification should still go through the declared helpers to preserve ownership rules.

## Dependencies and Integration Points
The header includes standard boolean, stdio, and sys/types headers. It is consumed by `camatch.c` and by encoder/traversal code that needs per-directory match state.

## Risks
The public structure makes ABI and invariant changes risky. Callers can bypass copy-on-write by mutating fields directly. `ca_match_children()` treats `NULL` as empty, which is convenient but can mask missing initialization.

## Test Signals
`test/test-camatch.c` directly validates several structure fields and API outcomes. Compile-time consumers also exercise this header through `caencoder.c`.
