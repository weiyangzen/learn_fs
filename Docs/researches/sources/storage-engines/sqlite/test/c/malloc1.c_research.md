# sources/storage-engines/sqlite/test/c/malloc1.c

## Purpose
`malloc1.c` is a minimal smoke test for SQLite memory allocation through the public API. It ensures `sqlite3_malloc()` works in a standalone program, including builds where automatic initialization is omitted.

## Important APIs, Types, and Functions
The file uses `sqlite3_initialize()` when `SQLITE_OMIT_AUTOINIT` is defined, then calls `sqlite3_malloc(32)` and `sqlite3_free()`.

## Control Flow
`main()` optionally initializes SQLite, allocates 32 bytes, returns failure if allocation returns NULL, frees the allocation, and exits success.

## State and Persistence Behavior
There is no database state. The only state exercised is SQLite's global allocator initialization and one heap allocation/free pair.

## Dependencies and Integration Points
It includes public `sqlite3.h` and is intended as a simple C test linked against the SQLite library under varying compile-time initialization settings.

## Risks and Edge Cases
The test does not verify allocator accounting, alignment, or zero-size behavior. Its main value is catching broken initialization/linkage or allocator replacement configurations.

## Test Signals
Exit status 0 indicates allocation and free succeeded. Exit status 1 indicates allocation failed unexpectedly.
