# sources/storage-engines/sqlite/src/vdbeapi.c

## Purpose

`vdbeapi.c` implements public and extension-facing APIs that operate on VDBE-backed prepared statements, SQL values, function contexts, result values, bindings, column accessors, statement metadata, virtual-table helper APIs, preupdate-hook value access, and scanstatus reporting. It is the bridge between SQLite's stable C API and the private `Vdbe`, `Mem`, cursor, frame, and scanstatus structures defined in `vdbeInt.h`.

The file does not implement the bytecode interpreter itself. Instead, it validates API usage, enters the connection mutex, translates C API operations into `Mem` and `Vdbe` state mutations, calls private execution/lifecycle helpers such as `sqlite3VdbeExec()`, `sqlite3VdbeReset()`, `sqlite3VdbeDelete()`, `sqlite3Reprepare()`, `sqlite3VdbeMem*()` functions, and returns public SQLite result codes.

## Important APIs and Functions

Statement lifecycle APIs:

- `sqlite3_finalize()` validates the statement, enters the connection mutex, fires any pending profile callback, resets execution state, deletes the VDBE, exits through `sqlite3ApiExit()`, and handles zombie connection close.
- `sqlite3_reset()` resets a statement to reusable state, rewinds it, fires profile callbacks, and returns the prior execution result.
- `sqlite3_clear_bindings()` releases every bind slot in `Vdbe.aVar`, sets each to NULL, and expires the VM if binding-sensitive plan bits are present.
- Deprecated `sqlite3_expired()` reports whether a statement needs recompile.

Safety and profiling helpers:

- `vdbeSafety()` and `vdbeSafetyNotNull()` detect NULL or finalized statements and log `SQLITE_MISUSE`.
- `invokeProfileCallback()` and `checkProfileCallback()` implement legacy profile and trace-v2 profile callbacks using elapsed VFS time when tracing is enabled.

Value APIs:

- `sqlite3_value_blob/text/text16/bytes/int/int64/double/type/subtype/encoding/nochange/frombind/pointer()` read `Mem` values, converting encodings or expanding zeroblobs as needed.
- `sqlite3_value_dup()` deep-copies string/blob values into an independent heap `sqlite3_value`, strips pointer subtypes from NULL pointer values, and avoids carrying dynamic ownership from the original. `sqlite3_value_free()` releases such copies.

Result APIs:

- `setResultStrOrError()` centralizes string/blob result storage, encoding conversion, length checks, and TOOBIG/NOMEM error propagation.
- `invokeValueDestructor()` calls application destructors for rejected inputs and sets TOOBIG when appropriate.
- `sqlite3_result_blob/blob64/text/text64/text16*()`, numeric/null/pointer/subtype/value/zeroblob result APIs, and error APIs write into `sqlite3_context.pOut`.
- `sqlite3_result_error_code()`, `sqlite3_result_error_toobig()`, and `sqlite3_result_error_nomem()` set `sqlite3_context.isError`, result text/null, debug app result code, and OOM state.
- `sqlite3ResultIntReal()` is a test-only hook to force `MEM_IntReal`.

Stepping APIs:

- `doWalCallbacks()` calls per-database WAL hooks after successful autocommit statement completion.
- `sqlite3Step()` performs the core `sqlite3_step()` state machine: starts ready statements, handles expiration, resets interrupts, starts trace timing, updates active/read/write counters, dispatches explain listing or `sqlite3VdbeExec()`, handles `SQLITE_ROW`, completion, WAL callbacks, saved-SQL error transfer, NOMEM normalization, and public result masking.
- `sqlite3_step()` wraps `sqlite3Step()` with statement validation, mutex entry, automatic schema reprepare up to `SQLITE_MAX_SCHEMA_RETRY`, reset after successful reprepare, and parser-error preservation on failed reprepare.

Function context and virtual-table helpers:

- `sqlite3_user_data()` and `sqlite3_context_db_handle()` expose function registration data and database handle.
- `sqlite3_vtab_nochange()` reports the virtual-table no-change marker in the function output slot.
- `sqlite3VdbeValueListFree()`, `valueFromValueList()`, `sqlite3_vtab_in_first()`, and `sqlite3_vtab_in_next()` implement typed-pointer iteration over ephemeral RHS values for virtual-table `IN` constraints.
- `sqlite3StmtCurrentTime()` caches statement time in `Vdbe.iCurrentTime`.
- `sqlite3_aggregate_context()` and `createAggContext()` allocate or return aggregate state stored in a `MEM_Agg` memory cell.
- `sqlite3_get_auxdata()` and `sqlite3_set_auxdata()` manage per-function/per-argument cached auxdata on `Vdbe.pAuxData`, with negative `iArg` acting as statement-wide undocumented cache scope.
- Deprecated `sqlite3_aggregate_count()` returns aggregate step count.

Column APIs:

- `sqlite3_column_count()` and `sqlite3_data_count()` report result shape and current-row availability.
- `columnNullValue()` returns a static aligned NULL `Mem` for invalid accesses.
- `columnMem()` validates row/column availability under mutex and returns either the row cell or static NULL while setting `SQLITE_RANGE`.
- `columnMallocFailure()` converts conversion-time allocation failure into statement `SQLITE_NOMEM` state and releases the mutex.
- `sqlite3_column_blob/bytes/bytes16/double/int/int64/text/text16/value/type()` call matching value APIs over `columnMem()`.
- `columnName()` returns result names, declaration types, origin metadata, or special EXPLAIN/EQP column names with UTF-8/UTF-16 conversion and OOM cleanup. The public `sqlite3_column_name*`, `sqlite3_column_decltype*`, and optional metadata name APIs are thin wrappers.

Binding APIs:

- `vdbeUnbind()` validates statement state, rejects busy statements, checks parameter range, releases the existing bind value, sets NULL, clears db error state, and expires the VM if that parameter affects query planning.
- `bindText()` handles common text/blob binding, destructor ownership, encoding conversion, API-exit error normalization, and mutex release.
- `sqlite3_bind_blob/blob64/double/int/int64/null/pointer/text/text64/text16/value/zeroblob/zeroblob64()` populate `Vdbe.aVar`.
- `sqlite3_bind_parameter_count()`, `sqlite3_bind_parameter_name()`, `sqlite3VdbeParameterIndex()`, and `sqlite3_bind_parameter_index()` expose bind slot metadata via `VList`.
- `sqlite3TransferBindings()` and deprecated `sqlite3_transfer_bindings()` move bind `Mem` values between compatible statements and expire both statements when needed.

Statement metadata APIs:

- `sqlite3_db_handle()`, `sqlite3_stmt_readonly()`, `sqlite3_stmt_isexplain()`, `sqlite3_stmt_explain()`, `sqlite3_stmt_busy()`, `sqlite3_next_stmt()`, `sqlite3_stmt_status()`, `sqlite3_sql()`, `sqlite3_expanded_sql()`, and optional `sqlite3_normalized_sql()` expose statement ownership, mutability, explain mode, execution state, connection statement list, counters, SQL text, expanded SQL, and normalized SQL.
- `sqlite3_stmt_explain()` can switch modes without reprepare if enough memory and EQP ops are already available; otherwise it reprepares saved SQL.
- `sqlite3_stmt_status(SQLITE_STMTSTATUS_MEMUSED)` uses `sqlite3VdbeDelete()` with `db->pnBytesFreed` and temporarily disables lookaside end pointers to measure memory without actually finalizing in the normal path.

Preupdate and scanstatus APIs:

- With `SQLITE_ENABLE_PREUPDATE_HOOK`, `vdbeUnpackRecord()`, `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, and `sqlite3_preupdate_blobwrite()` lazily decode old/new row values for preupdate callbacks, handle rowid versus WITHOUT ROWID mappings, default values for added columns, and update-depth/blob-write metadata.
- With `SQLITE_ENABLE_STMT_SCANSTATUS`, `sqlite3_stmt_scanstatus_v2()`, `sqlite3_stmt_scanstatus()`, and `sqlite3_stmt_scanstatus_reset()` expose loop counts, visit counts, estimates, names, explain text, select/parent ids, and cycle counts from `ScanStatus` and per-op counters.

## Control Flow

Most APIs follow a common shape: cast `sqlite3_stmt*` or `sqlite3_value*` to private `Vdbe*`/`Mem*`, validate misuse when API armor is enabled or where required, enter the owning database mutex, mutate or read private state, normalize errors through `sqlite3Error()`/`sqlite3ApiExit()`, and leave the mutex. The file assumes public SQLite threading semantics: prepared-statement operations are serialized by the connection mutex.

`sqlite3_step()` is the central control-flow path. It validates the VDBE, enters the mutex, calls `sqlite3Step()`, and loops only on `SQLITE_SCHEMA`. Reprepare copies compiler errors into the statement if recompilation fails; if recompilation succeeds, reset prepares the statement for another attempt and suppresses duplicate trace-statement emission by setting `minWriteFileFormat` to a sentinel value when appropriate.

`sqlite3Step()` itself enforces VDBE lifecycle transitions. READY statements may become RUN, HALT statements may auto-reset unless legacy `SQLITE_OMIT_AUTORESET` behavior applies, EXPLAIN statements route through `sqlite3VdbeList()`, and normal statements route through `sqlite3VdbeExec()`. `SQLITE_ROW` returns immediately with `pResultRow` populated. Completion clears `pResultRow`, invokes profile callbacks, runs WAL callbacks on autocommit success, and transfers saved-SQL errors.

Binding control flow is careful about mutex ownership. `vdbeUnbind()` enters the mutex and returns with it still held on success so the caller can install the new value atomically. On error it releases the mutex. `bindText()` and scalar bind wrappers must therefore release the mutex only after successful value installation, and must call application destructors themselves if unbind failed before SQLite took ownership.

Column access control flow is the inverse: `columnMem()` enters the mutex and returns a pointer while the mutex is still held; each public column accessor performs conversion and then calls `columnMallocFailure()` to handle OOM and release the mutex. This means every new column accessor must preserve the enter/leave pairing.

Preupdate old/new access lazily decodes data. Old values are unpacked from the btree payload only on first request. New INSERT values are unpacked from the serialized record register only on first request. New UPDATE values are copied into `PreUpdate.aNew` because returning a direct register pointer would let callers mutate encoding/state needed by the running VM.

## State and Persistence Behavior

`vdbeapi.c` mutates statement state but persists no database pages itself. Persistent database changes happen in the bytecode interpreter and btree/pager layers. This file controls when those changes are committed from the API perspective by stepping, resetting, finalizing, invoking WAL callbacks, and surfacing errors.

Important state transitions include `Vdbe.eVdbeState`, `pc`, `rc`, `pResultRow`, `expired`, active/read/write counters on `sqlite3`, saved SQL and normalized SQL caches, `aVar` bind values, `aCounter` statement-status counters, `aScan`/opcode execution counters, function aggregate `MEM_Agg` storage, auxdata linked lists, and preupdate caches.

Destructor ownership is a recurring persistence concern. Result and bind APIs must call application destructors if SQLite rejects input or cannot assume ownership. `SQLITE_STATIC`, `SQLITE_TRANSIENT`, and custom destructors have different behavior. Pointer values are represented as NULL values with subtype and terminator flags, so duplication deliberately removes pointer identity.

Statement time is stable within one run through `Vdbe.iCurrentTime`. Binding changes can set `expired` when `expmask` indicates the parameter may affect planning. Clear-bindings and transfer-bindings also honor this invalidation path.

## Dependencies and Integration Points

This file depends on `sqliteInt.h`, `vdbeInt.h`, and generated `opcodes.h`. It calls VDBE lifecycle/execution helpers, memory-cell helpers, btree payload and cursor operations, VFS time, WAL pager callbacks, schema reprepare, SQL expansion/normalization, virtual-table typed-pointer conventions, table/index column mapping helpers, record unpacking, default-expression evaluation, mutex/error/OOM utilities, and optional trace/profile hooks.

External integration surfaces include the public SQLite C API, application-defined SQL functions, virtual-table implementations, preupdate hooks, WAL hooks, trace/profile callbacks, statement scanstatus consumers, and deprecated compatibility APIs.

## Risks and Edge Cases

Mutex pairing is subtle. `vdbeUnbind()` and `columnMem()` intentionally return with the mutex held on success, leaving release to their callers. Any new path that returns early after these helpers risks deadlock. Conversely, releasing the mutex twice after a conversion failure would corrupt threading behavior.

`sqlite3_bind_zeroblob64()` enters the database mutex, then may call `sqlite3_bind_zeroblob()`, whose `vdbeUnbind()` also enters the same connection mutex. This relies on SQLite's mutex implementation and existing API pattern; changes to mutex kind or helper ownership would be risky.

`sqlite3_step()` automatic reprepare is bounded by `SQLITE_MAX_SCHEMA_RETRY`. Failure paths must preserve compiler error messages on the VDBE so later reset/finalize and `sqlite3_errmsg()` report the right condition. Saved SQL is required for many enhanced behaviors; legacy prepared statements without `SQLITE_PREPARE_SAVESQL` have narrower result-code contracts.

Value flags are security-sensitive. Pointer values require exact `MEM_Null|MEM_Term|MEM_Subtype`, subtype `'p'`, and matching pointer type string. `sqlite3_vtab_in_first/next()` additionally verifies the destructor is `sqlite3VdbeValueListFree()` to reject hostile fake typed pointers.

Text/blob length handling must respect 32-bit limits and UTF-16 even-byte truncation. Oversized `sqlite3_result_*64()` and bind paths must call destructors for rejected custom buffers. Encoding conversions can fail after returning column pointers, so `columnMallocFailure()` must set statement NOMEM state consistently.

Preupdate APIs have complex table mapping. Rowid tables, WITHOUT ROWID tables, generated storage column ordering, added columns with defaults, integer primary key aliases, and REAL affinity conversions all affect returned values. Mis-mapping can expose wrong old/new values to hooks.

Scanstatus cycle accounting supports direct address ranges and negative markers that search opcode properties. It must account for subprogram frames by walking to the root frame when a statement is currently inside triggers.

## Test Signals

High-value tests include finalizing NULL and valid statements, reset after row/done/error, profile and trace callbacks, auto-reset behavior after DONE, automatic reprepare after schema changes and binding-sensitive plan changes, WAL hook invocation after autocommit, and OOM during reprepare error copying.

Value/result tests should cover all storage classes, UTF-8 and UTF-16 conversion, subtype and pointer APIs, zeroblob expansion, oversized 64-bit lengths, destructor invocation on rejected inputs, strict subtype enforcement, `sqlite3_value_dup()` for strings/blobs/pointers, aggregate contexts, auxdata replacement/destruction, and stable `now` values.

Column/binding tests should cover out-of-range columns, calls before/after `SQLITE_ROW`, malloc failure during column text conversion, EXPLAIN/EQP column names, metadata APIs, binding while busy, out-of-range bind indexes, named parameters, binding transfer, clear-bindings expiration, pointer binding destructors, and zeroblob limit checks.

Virtual-table/preupdate/scanstatus tests should exercise `sqlite3_vtab_nochange()`, virtual-table `IN` iteration, hostile typed-pointer rejection, preupdate old/new values for INSERT/UPDATE/DELETE on rowid and WITHOUT ROWID tables, added-column defaults, update depth through triggers/FK actions, blob-write column reporting, scanstatus simple and complex modes, NCYCLE aggregation, reset of opcode counters, and feature-disabled builds.
