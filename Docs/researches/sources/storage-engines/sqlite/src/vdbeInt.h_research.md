# sources/storage-engines/sqlite/src/vdbeInt.h

## Purpose

`vdbeInt.h` is the private runtime header for SQLite's virtual database engine. It exposes the concrete layouts that are deliberately hidden from the public and semi-public VDBE interface: cursors, frames, memory cells, aggregate/function contexts, auxdata, scanstatus entries, preupdate-hook state, value-list iterators, and the full `Vdbe` statement object.

The header is included by the VDBE implementation files that execute bytecode, manage registers, decode records, call SQL functions, maintain cursor state, run triggers, expose C APIs, and collect statement metrics. It is not a persistence layer, but it defines the in-memory state that controls reads, writes, hooks, errors, and cleanup during a prepared statement's lifetime.

## Important APIs, Types, and Constants

`SQLITE_MAX_SCHEMA_RETRY` limits how many times a statement can be automatically reprepared after `SQLITE_SCHEMA`. `VDBE_DISPLAY_P4` centralizes whether P4 explain-display logic is compiled in.

`VdbeCursor` is the polymorphic cursor wrapper used by opcodes. `eCurType` distinguishes btree, sorter, virtual-table, and pseudo cursors. Shared fields track database index, null-row status, deferred seek state, table/index identity, ephemeral state, ordering, rowid generation, seek hits, cache status, prior seek result, sequence count, and optional column-used masks. The union stores a `BtCursor`, `sqlite3_vtab_cursor`, or `VdbeSorter`; other fields carry `KeyInfo`, root page, parsed record header offsets, payload pointers, decoded serial types, alternate cursor mappings, and optional large text/blob cache state.

`SZ_VDBECURSOR(N)` gives the rounded allocation size for a cursor with at least `N` fields. `IsNullCursor()` identifies null-only pseudo cursors. `CACHE_STALE` forces decoded-column caches invalid.

`VdbeTxtBlbCache` caches a large TEXT or BLOB column for a particular row offset, column, VM cache generation, and column-cache generation. This reduces repeated payload loads from btree pages for expensive column accesses.

`VdbeFrame` captures parent execution state when `OP_Program` enters a trigger/subprogram: parent op array, registers, cursors, once flags, recursion token, last rowid, auxdata, cursor/register counts, program counter, change counters, and child resource counts. Frames are owned by parent memory cells but delayed-free through `Vdbe.pDelFrame` to avoid recursive release paths.

`Mem` (`struct sqlite3_value`) is SQLite's internal SQL value container. It may carry integer, real, string, blob, null, pointer, aggregate, or zero-blob state. The flags split into type bits (`MEM_Null`, `MEM_Str`, `MEM_Int`, `MEM_Real`, `MEM_Blob`, `MEM_IntReal`), modifiers (`MEM_Term`, `MEM_Zero`, `MEM_Subtype`, `MEM_Cleared`, `MEM_FromBind`), and ownership bits (`MEM_Dyn`, `MEM_Static`, `MEM_Ephem`, `MEM_Agg`). `MEMCELLSIZE` identifies the prefix copied by shallow value duplication.

Helper macros such as `VdbeMemDynamic()`, `MemSetTypeFlag()`, `MemNullNochng()`, `memIsValid()`, and `ExpandBlob()` encode important invariants around dynamic ownership, type replacement, no-change virtual-table values, debug validity, and incremental-blob expansion.

`AuxData` backs `sqlite3_get_auxdata()` and `sqlite3_set_auxdata()`, associating an argument index and opcode with cached extension-owned data plus a destructor.

`sqlite3_context` is the internal function-call context. It stores the output `Mem`, function definition, aggregate memory cell, owning VDBE, opcode index, error code, desired encoding, skip flag, argument count, and argument array.

`ScanStatus` maps explain/loop metadata to opcode counters. It records explain opcode address, up to three opcode address ranges for cycle accounting, loop and visit counter opcode addresses, select id, estimated row count, and object name.

`DblquoteStr` tracks double-quoted string literals for normalized SQL builds.

`Vdbe` is the full prepared-statement object. Major fields include the owning `sqlite3`, statement linked-list pointers, parse context, bind count, register/cursor counts, cache generation, program counter, result code, change counts, current time, foreign-key counters, memory/register arrays, cursor array, bound variables, opcode array, result column metadata, current row, error message, variable-name list, trace start time, result column counts, write/read/explain flags, state enum, btree and lock masks, statement-status counters, saved SQL text, normalized SQL state, subprograms, frame lists, auxdata, and scanstatus array.

`VDBE_INIT_STATE`, `VDBE_READY_STATE`, `VDBE_RUN_STATE`, and `VDBE_HALT_STATE` define the allowed statement lifecycle states.

`PreUpdate` stores state for `sqlite3_preupdate_*()` APIs: current VM, cursor, operation, old record bytes, key info, unpacked old/new records, new-value register, blob-write column, old/new keys, cached old integer primary key, table and primary-key metadata, default-value cache, and inline keyinfo storage.

`ValueList` is passed to virtual tables as a typed pointer for `IN` constraints. It stores a btree cursor over ephemeral RHS values and a reusable output register.

The prototypes cover private VDBE behavior: cursor free/restore/moveto, serial-type handling, auxdata deletion, btree/index comparison, main execution and halt, encoding conversion, `Mem` copy/move/stringify/cast/grow/release/finalize operations, btree-to-Mem reads, frame restore/delete, preupdate hook dispatch, sorter operations, value-list free, write-counter assertions, shared-cache enter/leave, memory invariant checks, FK checks, debug printing, UTF-16 translation, and zeroblob expansion.

## Control Flow

During preparation, `Vdbe` starts in `VDBE_INIT_STATE` and accumulates opcodes, metadata, bind slots, and resource counts. `sqlite3VdbeMakeReady()` transitions it to ready state after allocating registers/cursors and setting execution metadata. `sqlite3_step()` then transitions ready statements to run state, `sqlite3VdbeExec()` interprets `aOp`, and `sqlite3VdbeHalt()`/reset logic returns the statement to halt or ready state.

Bytecode execution mutates `Vdbe.aMem`, `Vdbe.apCsr`, `Vdbe.pc`, `Vdbe.pResultRow`, change counters, foreign-key counters, and error fields. Cursor opcodes keep parsed-record caches in `VdbeCursor` synchronized with `Vdbe.cacheCtr`; deferred seeks allow seek operations to be postponed until data is actually needed.

Trigger and subprogram execution pushes `VdbeFrame` objects. The frame saves parent instruction/register/cursor arrays and counters, swaps in child arrays, then restores parent state when the subprogram returns. Frame deletion is deliberately delayed through `pDelFrame`.

SQL function opcodes populate `sqlite3_context` and `Mem` arguments, then extension code writes results back through result APIs. Aggregate functions keep their context in a `Mem` flagged `MEM_Agg`; auxdata persists on `Vdbe.pAuxData` until invalidated or halted.

Preupdate hooks are transient. DML opcodes populate `PreUpdate`, callbacks may request old/new values, and those APIs lazily unpack records or copy new registers into stable `Mem` arrays before returning pointers.

## State and Persistence Behavior

All structures in this header describe in-memory state. Persistent database effects are performed through btree/pager calls elsewhere, but this header defines the state that decides which btrees are touched (`btreeMask`, `lockMask`), whether a statement writes (`readOnly`, `nWrite`, `usesStmtJournal`), how changes are counted, and how constraints are tracked.

`Mem` ownership flags are persistence-like within a statement lifetime: dynamic strings, aggregates, zero-blobs, ephemeral pointers, and static pointers require different cleanup/copy behavior. The `MEM_FromBind` flag marks host-parameter origin, and `MEM_Null|MEM_Zero` is used as a no-change marker for virtual-table updates.

The cursor cache state (`cacheStatus`, `aOffset`, `aType`, `aRow`, `payloadSize`, `pCache`) persists across opcode executions until invalidated by cache generation changes, cursor movement, or row changes. `iCurrentTime` caches `now` for stable time values within one statement run.

## Dependencies and Integration Points

`vdbeInt.h` ties VDBE execution to most of SQLite core: btree cursors, pagers, virtual tables, sorters, schema objects, `KeyInfo`, unpacked records, parser structures, functions, collations, foreign-key logic, hooks, mutex/shared-cache control, UTF conversion, memory allocation, error handling, and optional scanstatus/profile/debug instrumentation.

It is consumed by `vdbe.c`, `vdbeapi.c`, `vdbeaux.c`, `vdbemem.c`, `vdbesort.c`, `vdbetrace.c`, record comparison logic, preupdate hook logic, virtual table integration, and debug/test builds.

## Risks and Edge Cases

The highest-risk surface is `Mem` flag consistency. Many operations depend on exact combinations of type, subtype, zero-blob, no-change, and ownership bits. Incorrect flag transitions can produce stale text encodings, missed destructors, double frees, invalid pointer values, or wrong SQL type results.

`VdbeCursor` has a split initialization contract: only early fields are zeroed on allocation, while later fields must be individually initialized before use. This saves work but makes new cursor paths sensitive to missed initialization. Flexible-array sizing through `SZ_VDBECURSOR()` must match `nField`.

Deferred frame deletion avoids recursion but means frame-owned resources survive until reset/halt. Bugs here can look like leaks or use-after-free when subprogram registers contain frame destructors.

Build flags change structure fields and APIs. `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_COLUMN_USED_MASK`, `SQLITE_DEBUG`, `SQLITE_OMIT_FLOATING_POINT`, UTF-16 options, and incremental-blob options all alter behavior. Tests need to cover representative feature matrices.

## Test Signals

Strong coverage comes from statements using btree, sorter, virtual-table, and pseudo cursors; large TEXT/BLOB column reads; deferred seeks; triggers and recursive triggers; aggregate functions and auxdata; pointer-valued SQL functions; virtual-table `xUpdate` no-change markers; `IN` constraints delivered to virtual tables; preupdate hooks for rowid and WITHOUT ROWID tables; foreign-key checks; UTF-16 conversion; zeroblob/incremental blob behavior; scanstatus metrics; and debug builds with memory invariant assertions enabled.
