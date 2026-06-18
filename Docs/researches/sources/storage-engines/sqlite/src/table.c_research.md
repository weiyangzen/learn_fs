# Research: sources/storage-engines/sqlite/src/table.c

## Purpose

`table.c` implements the legacy convenience APIs `sqlite3_get_table()` and
`sqlite3_free_table()` when `SQLITE_OMIT_GET_TABLE` is not defined. These APIs
run SQL through `sqlite3_exec()`, collect the entire result set into a
malloc-owned `char **` table, and return row and column counts to the caller.

This module is intentionally separate so builds that do not use the get-table
interface can avoid linking it.

## Important APIs, Types, And Functions

- `TabResult` is the accumulator passed as the `sqlite3_exec()` callback
  context. It stores the result vector, error text, allocated slots, row count,
  column count, used data slots, and callback return code.
- `sqlite3_get_table_cb()` is the row callback that grows the result vector,
  stores column names on the first row, checks column-count consistency across
  statements, copies row values, and stops execution on allocation failure.
- `sqlite3_get_table()` initializes `TabResult`, invokes `sqlite3_exec()`,
  handles callback aborts and exec errors, shrinks the result vector, and
  returns `&res.azResult[1]` to hide an internal slot containing the allocation
  size.
- `sqlite3_free_table()` reverses the pointer adjustment, reads the stored slot
  count from `azResult[-1]`, frees all non-null strings, and frees the result
  array.

## Control Flow

`sqlite3_get_table()` first validates the database handle and output pointer
under API armor, clears output arguments, allocates an initial 20-slot result
array, and reserves `azResult[0]` for metadata. It then calls `sqlite3_exec()`
with `sqlite3_get_table_cb()`.

The callback calculates how many slots the current invocation needs. On the
first data row it reserves space for both column names and row values; after
that it reserves only row values. It doubles previous allocation and adds the
current need when growth is required. The first row also initializes
`nColumn` and copies all column names with `sqlite3_mprintf()`. Later rows must
have the same column count; otherwise the callback sets a specific
incompatible-query error, stores `SQLITE_ERROR`, and aborts. Row values are
copied with `sqlite3_malloc64()` and `memcpy()`, preserving SQL NULLs as null
pointers.

After exec returns, `sqlite3_get_table()` stores `nData` in the hidden metadata
slot using pointer/int conversion macros. If execution was aborted by the
callback, it frees partial results, propagates the callback's own error message
where appropriate, sets `db->errCode`, and returns `res.rc`. If exec itself
failed, it frees the partial table and returns the exec code. On success it
shrinks the array to exactly the number of used slots and returns the pointer
one element past the metadata slot.

## State And Persistence Behavior

The module owns only transient heap state. It does not alter persistent database
format beyond whatever SQL text passed to `sqlite3_get_table()` executes via
`sqlite3_exec()`. The result allocation layout is an important ABI detail:
callers must free with `sqlite3_free_table()` rather than `sqlite3_free()`
because the visible pointer is offset by one slot.

The API stores column names as a first logical row before data rows, matching
SQLite's documented `sqlite3_get_table()` behavior. Even if a statement returns
zero rows, the result array still has internal metadata and a visible pointer
may be returned on success.

## Dependencies And Integration Points

The implementation depends on `sqliteInt.h`, `sqlite3_exec()`, SQLite memory
APIs (`sqlite3_malloc64()`, `sqlite3Realloc()`, `sqlite3_free()`,
`sqlite3_mprintf()`), string helpers (`sqlite3Strlen30()`), and internal
error-code conventions (`SQLITE_NOMEM_BKPT`, `SQLITE_ABORT`, `SQLITE_OK`).

It is a wrapper over the main exec callback interface rather than a separate
prepare/step/finalize path. That keeps behavior aligned with `sqlite3_exec()`
semantics for multi-statement SQL and callback aborts.

## Risks

The hidden metadata slot is fragile: any caller that passes a shifted or
manually modified pointer to `sqlite3_free_table()` can corrupt frees. The code
also relies on `sizeof(char*) >= sizeof(u32)` for storing `nData` in a pointer
slot, which is asserted.

Because the entire result set is materialized, this API can consume large
amounts of memory and is inappropriate for unbounded queries. Multi-statement
queries must return compatible column counts or the wrapper aborts with an
error specific to `sqlite3_get_table()`.

The callback uses `SQLITE_ABORT` detection through `(rc&0xff)==SQLITE_ABORT`,
so changes to extended result-code encoding or callback abort handling would
need care.

## Test Signals

Useful tests cover successful SELECTs with column-name row placement, SQL NULL
preservation as null pointers, zero-row results, multi-statement compatible and
incompatible result shapes, allocation-failure injection, propagation of
callback errors through `pzErrMsg`, `sqlite3_free_table(NULL)`, and API armor
misuse cases.
