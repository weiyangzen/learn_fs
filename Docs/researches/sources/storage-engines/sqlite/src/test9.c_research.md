<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test9.c -->
# sources/storage-engines/sqlite/src/test9.c

## Purpose
`test9.c` contains small C-only tests for obscure public C API behavior that would be awkward or meaningless to expose through generic Tcl bindings. It validates misuse handling, negative realloc semantics, and invalid collation encoding handling.

## Important APIs, Types, and Functions
`Sqlitetest9_Init()` registers `c_misuse_test`, `c_realloc_test`, and `c_collation_test`. These functions exercise `sqlite3_open()`, `sqlite3_close()`, `sqlite3_errcode()`, `sqlite3_prepare()`, `sqlite3_prepare_v2()`, UTF16 prepare variants when enabled, `sqlite3_malloc()`, `sqlite3_realloc()`, and `sqlite3_create_collation()`.

## Control Flow
`c_collation_test()` opens an in-memory database and calls `sqlite3_create_collation()` with an invalid encoding value `456`, expecting `SQLITE_MISUSE`. `c_realloc_test()` allocates five bytes and expects `sqlite3_realloc(p, -1)` to free the allocation and return null. `c_misuse_test()` opens then closes an in-memory handle, invokes selected APIs on the closed handle, and verifies they return `SQLITE_MISUSE`; prepare tests also assert that the statement output pointer is zeroed.

## State and Persistence Behavior
All databases are in-memory and temporary. The misuse test deliberately keeps a closed database pointer to validate API armor or misuse detection. No durable files are touched. Memory state is checked by observing that negative realloc releases ownership.

## Dependencies and Integration Points
The file uses `sqliteInt.h`, `tclsqlite.h`, public SQLite APIs, Tcl object command registration, and compile-time `SQLITE_OMIT_UTF16`. It integrates with the broader testfixture as commands returning Tcl success or an error naming the failing function.

## Risks
The closed-handle misuse checks depend on SQLite preserving enough sentinel state after `sqlite3_close()` for misuse detection. That is intentional but fragile if allocator/debug settings change. The tests assert pointer-zeroing, so release builds without assertions still rely on return-code checks while debug builds catch stronger invariants.

## Test Signals
Success is silent Tcl OK. Failures return `Error testing function: <api>`. Useful coverage includes `SQLITE_MISUSE` for invalid collation encodings and closed handles, null return from negative realloc, and statement pointer nullification after prepare misuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test9.c -->
