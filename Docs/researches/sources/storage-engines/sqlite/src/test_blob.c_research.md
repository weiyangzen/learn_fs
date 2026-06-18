<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_blob.c -->
# sources/storage-engines/sqlite/src/test_blob.c

## Purpose
`test_blob.c` exposes incremental BLOB APIs to Tcl in ways that supplement the normal Tcl channel interface. It can open blob handles, close them, read/write arbitrary offsets and sizes, and accept either raw pointer strings or Tcl incrblob channel names.

## Important APIs, Types, and Functions
Registered commands are `sqlite3_blob_open`, `sqlite3_blob_close`, `sqlite3_blob_bytes`, `sqlite3_blob_read`, and `sqlite3_blob_write`. Helpers include `ptrToText()`, `blobHandleFromObj()`, and `blobStringFromObj()`. The file uses `sqlite3_blob_open()`, `sqlite3_blob_close()`, `sqlite3_blob_bytes()`, `sqlite3_blob_read()`, `sqlite3_blob_write()`, `getDbPointer()`, and `sqlite3TestTextToPtr()`.

## Control Flow
`test_blob_open()` resolves a database handle, parses database/table/column/rowid/flags, and either stores the opened `sqlite3_blob*` pointer string in a Tcl variable or deliberately calls `sqlite3_blob_open()` with a null output pointer when the variable name is empty. `blobHandleFromObj()` recognizes `incrblob_` channel names, flushes and seeks the channel, extracts its instance data, or decodes a pointer string. Read allocates a Tcl buffer, calls `sqlite3_blob_read()`, and returns a byte array. Write takes a Tcl byte array and optional override length and calls `sqlite3_blob_write()`.

## State and Persistence Behavior
Open blob handles are external resources that must be closed. Handles obtained from Tcl channels remain owned by the channel, although this test code can operate on the underlying pointer. Writes mutate the referenced row's BLOB storage through SQLite's incremental blob mechanism and are constrained by the blob size and transaction state.

## Dependencies and Integration Points
The file compiles only when incremental blob support is present. It integrates with Tcl SQLite database handles, the Tcl channel implementation for `[db incrblob]`, SQLite pointer-string utilities, and symbolic error names.

## Risks
The static buffer in `ptrToText()` is overwritten by each call. Pointer-string blob handles have no lifetime checks. Channel extraction assumes Tcl channel instance data layout used by SQLite's incrblob channel. The optional `NDATA` argument to write can exceed the Tcl byte-array length, causing SQLite to read past the supplied buffer if misused; tests should use it only for deliberate misuse coverage.

## Test Signals
Signals include stored pointer text, `SQLITE_*` error names for invalid offsets or closed handles, byte-exact read results, byte count from `sqlite3_blob_bytes()`, and persistence of writes observed by SQL queries or subsequent blob reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_blob.c -->
