# sources/storage-engines/foundationdb/bindings/c/test/fdb_c90_test.c

## Purpose
Minimal C compilation/runtime smoke test for the public FoundationDB C header under a C-style translation unit.

## Important APIs, types, and functions
Defines `FDB_API_VERSION 800`, includes `foundationdb/fdb_c.h`, and calls `fdb_select_api_version`.

## Control flow
`main` ignores arguments, selects the API version, and returns zero.

## State and persistence behavior
No network, database, file, or cluster state is touched.

## Dependencies and integration points
Depends only on the public C API header and C compiler compatibility.

## Risks and test signals
Any accidental C++ dependency or C90-incompatible header change should fail compilation.
