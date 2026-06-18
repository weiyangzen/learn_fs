# Research: sources/storage-engines/sqlite/src/status.c

## Purpose

`status.c` implements SQLite's global `sqlite3_status()` /
`sqlite3_status64()` APIs and per-connection `sqlite3_db_status()` /
`sqlite3_db_status64()` APIs. It records memory/page-cache counters, exposes
current and high-water values, and computes connection-local statistics such as
lookaside usage, schema memory, statement memory, pager cache activity,
temporary spill bytes, and deferred foreign-key state.

The file is deliberately small but important for observability. Many counters
are maintained by other subsystems and read here under the same mutexes that
protect updates.

## Important APIs, Types, And Data

- `sqlite3StatValueType` is `sqlite3_int64` on pointer sizes greater than four
  bytes and `u32` otherwise.
- `sqlite3StatType` contains `nowValue[10]` and `mxValue[10]`, the current and
  high-water values for global status verbs.
- `sqlite3Stat` is writable static data unless `SQLITE_OMIT_WSD` requires the
  `GLOBAL()` indirection through `wsdStat`.
- `statMutex[]` maps each global status verb to either the allocator mutex or
  the pcache1 mutex.
- `sqlite3StatusValue()`, `sqlite3StatusUp()`, `sqlite3StatusDown()`, and
  `sqlite3StatusHighwater()` are internal update/read helpers. They assert that
  callers hold the correct mutex.
- `sqlite3_status64()` and `sqlite3_status()` are public global status query
  interfaces. The 32-bit variant truncates the 64-bit results to `int`.
- `sqlite3LookasideUsed()` counts connection lookaside slots.
- `sqlite3_db_status64()` and `sqlite3_db_status()` are public
  connection-local status query interfaces.

## Control Flow

Global status updates are simple counter operations. The helper functions check
array bounds and mutex ownership in asserts, update `nowValue`, and optionally
advance or reset `mxValue`. `sqlite3_status64()` validates the verb, optionally
checks output pointers under API armor, enters the mutex selected by
`statMutex[]`, copies current/high-water values, resets the high-water value to
the current value if requested, and leaves the mutex.

Per-connection status is a switch inside `sqlite3_db_status64()` protected by
`db->mutex`:

- lookaside status counts slots on `pInit`, `pFree`, and, when enabled, the
  two-size lookaside lists. Resetting folds free lists back into init lists so
  the next high-water baseline changes;
- lookaside hit/miss counters return the accumulated high-water-style value and
  reset the selected `anStat` entry if requested;
- cache memory walks all `db->aDb[]` btrees, asks each pager for memory used,
  and optionally divides shared cache usage by the connection count;
- schema memory temporarily routes frees into `db->pnBytesFreed`, disables
  lookaside allocation by shrinking `lookaside.pEnd`, and calls schema object
  destructors to measure memory without actually losing the live schema;
- statement memory uses the same `pnBytesFreed` accounting trick around all
  VDBEs on the connection;
- cache hit/miss/write/spill totals are accumulated through
  `sqlite3PagerCacheStat()`;
- temporary spill bytes combine temp database pager writes converted to bytes
  with `db->nSpill`;
- deferred foreign-key status reports whether immediate or deferred constraint
  counters are nonzero.

Unknown per-connection verbs return `SQLITE_ERROR`.

## State And Persistence Behavior

The global `sqlite3Stat` object is process-local mutable state. It is not
persistent across process lifetime and is reset only by process initialization
or high-water reset calls. Updates are expected to happen from allocator or
page-cache code under the mutex selected for the status verb.

Connection status reads depend on live `sqlite3` state. Resetting some status
verbs mutates in-memory counters (`lookaside.anStat`, `db->nSpill`) or lookaside
bookkeeping lists, but it does not write database files. The schema and
statement memory calculations deliberately use SQLite's destructor paths in a
measurement mode driven by `db->pnBytesFreed`; their correctness depends on
those destructors honoring the counting convention and not actually releasing
live structures in this path.

## Dependencies And Integration Points

This file includes `sqliteInt.h` and `vdbeInt.h`. It integrates with:

- memory allocation status through `sqlite3MallocMutex()` and allocator update
  hooks;
- pcache status through `sqlite3Pcache1Mutex()`;
- btree/pager APIs such as `sqlite3BtreeEnterAll()`, `sqlite3BtreePager()`,
  `sqlite3PagerMemUsed()`, `sqlite3PagerCacheStat()`, and
  `sqlite3BtreeConnectionCount()`;
- schema hash tables and destructors (`sqliteHashFirst()`,
  `sqlite3DeleteTrigger()`, `sqlite3DeleteTable()`);
- VDBE ownership through `db->pVdbe` and `sqlite3VdbeDelete()`;
- lookaside allocator internals on `sqlite3.lookaside`.

The public API result codes are part of SQLite's stable C API, so behavior here
is visible to applications and testfixture scripts.

## Risks

The main risk is mutex discipline. Internal status helpers rely on asserts
rather than runtime locking, so callers must already hold the right mutex. A new
status verb must be added consistently to the arrays, mutex map, public enum
definitions, and update sites.

The measurement paths for schema and statement memory are subtle: they reuse
delete routines while diverting freed byte counts and temporarily disabling
lookaside. Changes to destructors, lookaside fields, or `pnBytesFreed` could
turn a measurement into a real free or undercount allocations.

The 32-bit wrappers mask 64-bit values with `0x7fffffff` for db-status and cast
for global status, so tests that compare very large counters need to use the
64-bit APIs.

## Test Signals

Strong tests include allocator/page-cache status increments under
threadsafe builds, high-water reset checks, API armor null-pointer checks,
lookaside reset behavior with both one-size and two-size lookaside builds,
schema and statement memory reporting with prepared statements and attached
databases, cache hit/miss/write/spill counters before and after reset, temp
buffer spill accounting, and deferred foreign-key status inside and after
transactions.
