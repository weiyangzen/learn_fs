# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/continuation.c

## Purpose
`continuation.c` is a checked-in expected C output for an `.et` file containing a multi-line continued message.

## Important APIs, Types, and Functions
It defines `text[]`, `et_ovk_error_table`, a static fallback `link`, `initialize_ovk_error_table()`, and `initialize_ovk_error_table_r()`.

## Control Flow
The initializer delegates global registration to the list-aware variant. The list-aware initializer scans for the same `text` array, appends a malloc-backed or static fallback node, and preserves idempotence.

## State, Persistence, Dependencies, Risks, and Test Signals
State is `_et_list` and optional heap/static registration node. Dependencies are generated layout compatibility with com_err. Risks are fallback static link reuse and no explicit locking in generated code. The primary test signal is diff equality with `compile_et` output for the continuation fixture.
