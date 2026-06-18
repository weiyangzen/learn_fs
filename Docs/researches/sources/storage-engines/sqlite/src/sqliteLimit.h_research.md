# Research: sources/storage-engines/sqlite/src/sqliteLimit.h

## Purpose

`sqliteLimit.h` centralizes SQLite's compile-time resource limits and default
capacity policy. It is not executable code; it is a configuration contract used
by parser, VDBE, pager, btree, function, trigger, page-cache, and public limit
APIs to keep resource use bounded and file-format assumptions consistent.

The file provides default values when the build has not supplied
`-DSQLITE_MAX_*` or related options, and it enforces a few hard caps with
preprocessor errors or normalization. These constants shape both security
posture and compatibility: lowering them can constrain hostile SQL inputs,
while raising some values is impossible because internal fields, varint
encodings, page layout, or 32-bit signed lengths would no longer be safe.

## Important Limits And Macros

- `SQLITE_MAX_LENGTH` defaults to 1,000,000,000 bytes and bounds TEXT, BLOB,
  row, and index-record sizes. `SQLITE_MIN_LENGTH` records the minimum runtime
  length-limit value accepted elsewhere.
- `SQLITE_MAX_ALLOCATION_SIZE` caps one `sqlite3_malloc()` or
  `sqlite3_realloc()` request. It defaults to `2147483391`, slightly below
  2 GiB, and is rejected above that value to preserve a 256-byte overflow
  margin.
- `SQLITE_MAX_COLUMN` defaults to 2000 and is capped at 32767 because column
  counts and related limits are stored in signed 16-bit fields in several
  places.
- `SQLITE_MAX_SQL_LENGTH`, `SQLITE_MAX_EXPR_DEPTH`, and
  `SQLITE_MAX_PARSER_DEPTH` bound parse input size, expression recursion, and
  parser stack depth.
- `SQLITE_MAX_COMPOUND_SELECT`, `SQLITE_MAX_VDBE_OP`, and
  `SQLITE_MAX_FUNCTION_ARG` bound statement complexity. The function argument
  count defaults to 1000 and is constrained by a 32767 hard storage limit.
- `SQLITE_DEFAULT_CACHE_SIZE` and `SQLITE_DEFAULT_WAL_AUTOCHECKPOINT` supply
  default page-cache and WAL checkpoint policy.
- `SQLITE_MAX_ATTACHED` defaults to 10 and is documented as limited to 125
  because attached database indexes fit in a signed 8-bit counter after
  reserving slots for `main` and `temp`.
- `SQLITE_MAX_VARIABLE_NUMBER` defaults to 32766, avoiding extra `Expr` storage
  for very large parameter indexes.
- `SQLITE_MAX_PAGE_SIZE` is forcibly set to 65536 even if a build attempts to
  override it. This preserves file-format compatibility around 16-bit offsets
  and crash recovery.
- `SQLITE_DEFAULT_PAGE_SIZE` and `SQLITE_MAX_DEFAULT_PAGE_SIZE` are normalized
  so defaults never exceed `SQLITE_MAX_PAGE_SIZE`, and the automatic default
  maximum never drops below the explicit default.
- `SQLITE_MAX_PAGE_COUNT`, `SQLITE_MAX_LIKE_PATTERN_LENGTH`, and
  `SQLITE_MAX_TRIGGER_DEPTH` provide default caps for database file pages,
  pattern matching input, and trigger recursion.

## Control Flow And Validation Behavior

The control flow is preprocessor-only. Most definitions follow the same pattern:
if a macro is not already defined by the build, define a conservative default.
Some macros add an `#elif` or `#if` guard to reject unsupported values. Page-size
macros are more assertive: any external `SQLITE_MAX_PAGE_SIZE` definition is
undefined and replaced with 65536, while page-size defaults are clamped by
preprocessor rewrites.

This file therefore runs before C compilation of the SQLite core. Runtime code
does not call into it, but many runtime decisions assume the invariants it
establishes. A bad value here usually causes either compile failure or latent
breakage in allocation, parser recursion, statement construction, or file I/O.

## State And Persistence Behavior

The header maintains no runtime state and persists nothing directly. Its values
can affect persistent database shape indirectly. `SQLITE_MAX_PAGE_SIZE`,
`SQLITE_DEFAULT_PAGE_SIZE`, and `SQLITE_MAX_PAGE_COUNT` interact with database
header fields and pager/btree decisions. The forced 64 KiB page-size maximum is
especially important because a process compiled with incompatible page limits
could otherwise fail to roll back a transaction created by another build.

Other values affect only per-process resource ceilings, such as expression
depth, SQL text length, and allocation size. Those limits can influence which
schemas or SQL statements a given build accepts.

## Dependencies And Integration Points

`sqliteLimit.h` is consumed through SQLite internal headers, primarily
`sqliteInt.h`, and feeds:

- public `sqlite3_limit()` categories such as length, SQL length, columns,
  expression depth, compound select terms, variable number, function arguments,
  LIKE/GLOB pattern length, and trigger depth;
- parser and code generator arrays and recursion checks;
- VDBE program construction and function invocation checks;
- btree and pager page-size logic;
- WAL auto-checkpoint defaults and page-cache default sizing.

The comments include requirement tags for cache-size defaults, so this file is
also part of SQLite's evidence-backed documentation/test matrix.

## Risks

The highest-risk changes are values tied to storage widths or file format:
`SQLITE_MAX_COLUMN`, `SQLITE_MAX_FUNCTION_ARG`, `SQLITE_MAX_ATTACHED`,
`SQLITE_MAX_VARIABLE_NUMBER`, and all page-size/count constants. Increasing
limits without auditing downstream integer types can introduce truncation,
overflow, parser stack exhaustion, or incompatible database files.

Lowering limits is usually safer but can break applications or tests that rely
on SQLite's documented defaults. Raising `SQLITE_MAX_ALLOCATION_SIZE` is
explicitly blocked above the hard cap; changing that guard would reduce defense
against 32-bit signed overflow bugs.

## Test Signals

Useful validation signals include compile-time tests that deliberately override
macros near hard boundaries, `sqlite3_limit()` API tests, parser stress tests
for deeply nested expressions and compound selects, large BLOB/TEXT boundary
tests, function argument count tests, and database open/recovery tests for page
sizes up to 65536. Requirement tests should continue to verify the documented
default cache size and WAL auto-checkpoint values.
