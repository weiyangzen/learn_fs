# sources/storage-engines/sqlite/src/fault.c

## Purpose

`fault.c` provides the small test/build-support layer behind SQLite's "benign malloc failure" concept. It lets fault-injection harnesses register callbacks that bracket allocations whose failure is recoverable. The main in-tree user pattern is code that can keep operating after an allocation fails, such as hash-table growth in `hash.c`; those call sites mark the allocation window so tests do not treat the injected failure as a required `SQLITE_NOMEM` path.

## Important APIs, Types, And Functions

The file is compiled only when `SQLITE_UNTESTABLE` is not defined. `BenignMallocHooks` stores `xBenignBegin` and `xBenignEnd` function pointers in `sqlite3Hooks`, a `SQLITE_WSD` global. `sqlite3BenignMallocHooks()` installs the callbacks. `sqlite3BeginBenignMalloc()` and `sqlite3EndBenignMalloc()` invoke the callbacks if present.

The `SQLITE_OMIT_WSD` branch routes access through `GLOBAL(BenignMallocHooks, sqlite3Hooks)`, matching SQLite's writable-static-data abstraction for platforms that cannot directly use globals.

## Control Flow

Registration is direct assignment into the global hook pair. A benign allocation site calls `sqlite3BeginBenignMalloc()`, performs the allocation, then calls `sqlite3EndBenignMalloc()`. Each wrapper resolves the writable static state, checks for a non-null callback, and calls it. There is no nesting counter here; any nesting semantics belong to the registered test allocator or instrumentation.

## State And Persistence Behavior

State is process-global and in-memory only. It is not database state, is not persisted to the database file, and is not per connection. Because callbacks are global, test configuration affects all SQLite connections in the process.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, `SQLITE_WSD`, `GLOBAL()`, and the `SQLITE_UNTESTABLE` build gate. `hash.c` integrates with this facility around benign rehash allocations. SQLite test controls and memory fault injection can install hooks to avoid flagging these recoverable allocations as hard failures.

## Risks

The main risk is misclassifying an allocation as benign when callers actually require success for correctness. Another risk is callback globality: concurrent tests or multiple SQLite users in one process share the hook pair. Since this file does not count nesting, hook implementations must tolerate nested begin/end sequences if callers introduce them. Builds with `SQLITE_UNTESTABLE` omit the API body, so tests that depend on hooks must use a testable build.

## Test Signals

Useful tests inject malloc failures during hash-table resizing and verify operations continue with the old table shape. Platform coverage should include normal writable static data and `SQLITE_OMIT_WSD` builds. Test builds should also verify null hooks are harmless and that begin/end callback ordering is balanced across recoverable allocation sites.
