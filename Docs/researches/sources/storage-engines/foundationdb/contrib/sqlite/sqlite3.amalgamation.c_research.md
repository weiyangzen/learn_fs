# Research: sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008406`: lines 1-6110, `Docs/researches/chunks/subset-b-008406_research.md`
- `subset-b-008407`: lines 6111-14968, `Docs/researches/chunks/subset-b-008407_research.md`
- `subset-b-008408`: lines 14969-22849, `Docs/researches/chunks/subset-b-008408_research.md`
- `subset-b-008409`: lines 22850-30612, `Docs/researches/chunks/subset-b-008409_research.md`
- `subset-b-008410`: lines 30613-37428, `Docs/researches/chunks/subset-b-008410_research.md`
- `subset-b-008411`: lines 37429-45048, `Docs/researches/chunks/subset-b-008411_research.md`
- `subset-b-008412`: lines 45049-52795, `Docs/researches/chunks/subset-b-008412_research.md`
- `subset-b-008413`: lines 52796-60569, `Docs/researches/chunks/subset-b-008413_research.md`
- `subset-b-008414`: lines 60570-68379, `Docs/researches/chunks/subset-b-008414_research.md`
- `subset-b-008415`: lines 68380-75677, `Docs/researches/chunks/subset-b-008415_research.md`
- `subset-b-008416`: lines 75678-83001, `Docs/researches/chunks/subset-b-008416_research.md`
- `subset-b-008417`: lines 83002-89544, `Docs/researches/chunks/subset-b-008417_research.md`
- `subset-b-008418`: lines 89545-96988, `Docs/researches/chunks/subset-b-008418_research.md`
- `subset-b-008419`: lines 96989-105142, `Docs/researches/chunks/subset-b-008419_research.md`
- `subset-b-008420`: lines 105143-110689, `Docs/researches/chunks/subset-b-008420_research.md`

## Chunk Research

### subset-b-008406: lines 1-6110

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 1-6110

## Scope

This chunk covers the beginning of the FoundationDB-vendored SQLite 3.7.6 amalgamation. It includes the local compile-time settings, the embedded internal header stack (`sqliteInt.h`, `sqliteLimit.h`, `hash.h`, `parse.h`, `btree.h`, `vdbe.h`, `pager.h`, `pcache.h`, `os.h`, `mutex.h`), the main in-memory schema/parser/VDBE declarations, `global.c`, `ctime.c`, and the start of `status.c` through the early private VDBE runtime definitions.

## Purpose

The covered lines establish the compilation contract and most of the private type/API surface used by the rest of the amalgamation. They do not implement full SQL execution yet; instead they define the limits, tokens, opcodes, subsystem APIs, global configuration, and central runtime structures that later source sections consume.

The top of the file is FoundationDB-specific compared with a stock SQLite amalgamation:

- `NDEBUG` is force-defined before the normal SQLite debug negotiation.
- `SQLITE_THREADSAFE` is set to `0`, selecting a non-threadsafe/no-mutex build at compile time.
- `ENABLE_SCRATCHALLOC_CHECK` is set to `0`.
- `SQLITE_OMIT_SHARED_CACHE` is set to `1`.
- `SQLITE_FILE_HEADER` is changed to `"FoundationDB100"`, which affects database file identity and is a persistence compatibility boundary.
- `HAVE_USLEEP` is set to `1`.

The chunk then sets `SQLITE_CORE`, `SQLITE_AMALGAMATION`, `SQLITE_PRIVATE`, and `SQLITE_API`, making the rest of the file compile as SQLite core code in a single translation unit.

## Compile-Time Limits and Configuration

`sqliteLimit.h` defines the core size and complexity limits that later parser, VDBE, pager, and schema code enforce or assume:

- `SQLITE_MAX_LENGTH`, `SQLITE_MAX_SQL_LENGTH`, and `SQLITE_MAX_LIKE_PATTERN_LENGTH` bound input, row, and pattern sizes.
- `SQLITE_MAX_COLUMN`, `SQLITE_MAX_FUNCTION_ARG`, `SQLITE_MAX_VARIABLE_NUMBER`, `SQLITE_MAX_COMPOUND_SELECT`, and `SQLITE_MAX_EXPR_DEPTH` bound parse tree and VM complexity.
- `SQLITE_DEFAULT_CACHE_SIZE`, `SQLITE_DEFAULT_TEMP_CACHE_SIZE`, `SQLITE_DEFAULT_WAL_AUTOCHECKPOINT`, and page-size constants influence default pager/cache behavior.
- `SQLITE_MAX_PAGE_SIZE` is forcibly set to `65536` even if previously defined, preserving page-format compatibility assumptions.
- `SQLITE_MAX_ATTACHED` is capped at the default 10, with comments noting a hard 30 limit due to bitmaps.
- `SQLITE_DEFAULT_AUTOVACUUM`, `SQLITE_TEMP_STORE`, `SQLITE_DEFAULT_RECURSIVE_TRIGGERS`, file-format constants, and default page/count settings define initial database behavior.

The chunk also defines portability and instrumentation macros:

- Large-file support macros (`_FILE_OFFSET_BITS=64`, `_LARGEFILE_SOURCE`) unless disabled.
- `SQLITE_INT_TO_PTR` and `SQLITE_PTR_TO_INT` variants for compiler-specific pointer/integer casts.
- `ALWAYS`, `NEVER`, `testcase`, `TESTONLY`, and `VVA_ONLY` for defensive code and coverage/debug builds.
- Endianness macros, integer typedefs (`i64`, `u64`, `u32`, `u16`, `u8`, etc.), alignment macros, and integer bounds.
- `SQLITE_DEFAULT_MEMSTATUS` is locally defaulted to `0` with an explicit FIXME noting that enabling it would improve memory tracking for SQLite threads but causes mutex contention. In this build, `SQLITE_THREADSAFE=0` and omitted mutexes make that tradeoff especially important to validate against the wider FoundationDB integration.

## Important Types and Interfaces

### Hash Tables

The embedded `hash.h` defines:

- `Hash`, a generic hash table with a global doubly linked element list plus optional bucket table.
- `HashElem`, storing linked-list pointers, `data`, and key bytes.
- `sqlite3HashInit`, `sqlite3HashInsert`, `sqlite3HashFind`, and `sqlite3HashClear`.
- Iteration macros `sqliteHashFirst`, `sqliteHashNext`, and `sqliteHashData`.

These hash tables are later used for schemas, functions, collations, triggers, foreign keys, and virtual table modules.

### Parser Tokens and VDBE Opcodes

`parse.h` maps SQL grammar tokens (`TK_SELECT`, `TK_INSERT`, `TK_VARIABLE`, `TK_FUNCTION`, etc.) to integer constants. Expression nodes reuse these token numbers as expression opcodes.

`vdbe.h` defines the public-internal VDBE instruction surface:

- `Vdbe`, `VdbeOp`, `VdbeOpList`, `SubProgram`, `Mem`, `VdbeFunc`.
- `VdbeOp` fields: `opcode`, `p1`, `p2`, `p3`, `p4`, `p4type`, `p5`, and optional debug/profile fields.
- `P4_*` ownership/type constants, including dynamic/static strings, collations, function definitions, key info, memory cells, virtual tables, integer/real payloads, and trigger subprograms.
- `COLNAME_*` result metadata slots.
- `ADDR()` relative-address encoding used by `sqlite3VdbeAddOpList()`.
- `opcodes.h` constants from `OP_Goto` through `OP_Explain`, plus `OPFLG_*` metadata and `OPFLG_INITIALIZER`.
- VDBE construction and mutation APIs such as `sqlite3VdbeCreate`, `sqlite3VdbeAddOp*`, `sqlite3VdbeChangeP*`, `sqlite3VdbeMakeReady`, `sqlite3VdbeFinalize`, `sqlite3VdbeReset`, `sqlite3VdbeSetColName`, `sqlite3VdbeRecordUnpack`, and `sqlite3VdbeRecordCompare`.

The opcode list shows the control-flow bridge between parser/codegen and persistence: transaction opcodes (`OP_Transaction`, `OP_Savepoint`, `OP_AutoCommit`), B-tree cursor opcodes (`OP_OpenRead`, `OP_OpenWrite`, `OP_Seek*`, `OP_Insert`, `OP_Delete`), schema opcodes (`OP_CreateTable`, `OP_ParseSchema`, `OP_DropTable`), WAL/checkpoint opcodes, virtual table opcodes, and trigger/subprogram opcodes.

### B-tree, Pager, Page Cache, and VFS

`btree.h` exposes the logical storage layer:

- Open/close/configuration APIs: `sqlite3BtreeOpen`, `sqlite3BtreeClose`, `sqlite3BtreeSetCacheSize`, `sqlite3BtreeSetSafetyLevel`, `sqlite3BtreeSetPageSize`, `sqlite3BtreeMaxPageCount`.
- Transaction APIs: `sqlite3BtreeBeginTrans`, `sqlite3BtreeCommitPhaseOne`, `sqlite3BtreeCommitPhaseTwo`, `sqlite3BtreeCommit`, `sqlite3BtreeRollback`, `sqlite3BtreeBeginStmt`, `sqlite3BtreeSavepoint`.
- Schema/meta APIs: `sqlite3BtreeGetMeta`, `sqlite3BtreeUpdateMeta`, `sqlite3BtreeSchema`, `sqlite3BtreeSchemaLocked`, `BTREE_*` meta indices.
- Cursor APIs: `sqlite3BtreeCursor`, `sqlite3BtreeMovetoUnpacked`, `sqlite3BtreeInsert`, `sqlite3BtreeDelete`, `sqlite3BtreeFirst/Next/Last/Previous`, key/data fetch APIs, and rowid cache APIs.
- Integrity and vacuum APIs: `sqlite3BtreeIntegrityCheck`, `sqlite3BtreeIncrVacuum`, `sqlite3BtreeSetAutoVacuum`, `sqlite3BtreeGetAutoVacuum`.

`pager.h` exposes file-page persistence and rollback/WAL behavior:

- `Pager` and `DbPage` types.
- Journal mode constants `PAGER_JOURNALMODE_DELETE`, `PERSIST`, `OFF`, `TRUNCATE`, `MEMORY`, and `WAL`.
- Open/configuration APIs: `sqlite3PagerOpen`, `sqlite3PagerClose`, `sqlite3PagerSetBusyhandler`, `sqlite3PagerSetPagesize`, `sqlite3PagerSetCachesize`, `sqlite3PagerSetSafetyLevel`, `sqlite3PagerLockingMode`, `sqlite3PagerSetJournalMode`.
- Page access APIs: `sqlite3PagerAcquire`, `sqlite3PagerGet`, `sqlite3PagerLookup`, `sqlite3PagerRef`, `sqlite3PagerUnref`, `sqlite3PagerWrite`, `sqlite3PagerDontWrite`, `sqlite3PagerMovepage`, `sqlite3PagerGetData`, `sqlite3PagerGetExtra`.
- Transaction APIs: `sqlite3PagerBegin`, `sqlite3PagerCommitPhaseOne`, `sqlite3PagerCommitPhaseTwo`, `sqlite3PagerRollback`, savepoint APIs, shared/exclusive locking APIs, and checkpoint/WAL APIs.

`pcache.h` defines `PgHdr` and `PCache`:

- `PgHdr` stores `pData`, `pExtra`, dirty-list links, page number, owning `Pager`, flags, refcount, and cache pointer.
- Flags include `PGHDR_DIRTY`, `PGHDR_NEED_SYNC`, `PGHDR_NEED_READ`, `PGHDR_DONT_WRITE`, and a FoundationDB-visible addition `PGHDR_ZERO_COPY`, used for pages read through `xReadZeroCopy` and released with `xReleaseZeroCopy`.
- APIs cover page cache initialization, buffer setup, fetch/release/drop/dirty/clean/move/truncate, dirty-list retrieval, refcounting, cache-size hints, memory release, and test stats.

`os.h` abstracts platform I/O:

- Detects Unix, Windows, OS/2, or other VFS targets.
- Defines lock levels (`NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`) and lock-byte layout (`PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, `SHARED_SIZE`).
- Provides `sqlite3Os*` wrappers around `sqlite3_file` and `sqlite3_vfs` methods, including read/write/truncate/sync/lock/shm/randomness/sleep/time/open/delete/access/full-pathname/dlopen support.
- Defines `SQLITE_FCNTL_DB_UNCHANGED`, which is an integration hook for file-control behavior.

### Mutexes and Threading

Because this file sets `SQLITE_THREADSAFE 0`, `mutex.h` selects `SQLITE_MUTEX_OMIT`. In this mode all public/internal mutex operations become no-op macros and `sqlite3_mutex_alloc()` returns a sentinel pointer. Shared-cache enter/leave macros are also no-ops because `SQLITE_OMIT_SHARED_CACHE` is set.

This substantially narrows the valid embedding model: the same SQLite build must not be used concurrently through shared mutable state unless the caller provides stronger external serialization.

### Core Database and Schema Structures

The chunk defines central durable/in-memory metadata structures:

- `Db`: per-attached-database handle with `zName`, `Btree *pBt`, transaction state, safety level, and `Schema *pSchema`.
- `Schema`: schema cookie, table/index/trigger/foreign-key hash tables, autoincrement sequence table, file format, encoding, flags, and cache size.
- `sqlite3`: the database connection object. It stores VFS, `Db` array, flags, autocommit state, error state, limits, initialization state, active VDBEs, callbacks, lookaside allocator, authorization/progress/virtual table state, function/collation registries, busy handler, default backends, savepoints, deferred FK counters, and optional unlock-notify state.
- `Lookaside` and `LookasideSlot`: fixed-size per-connection allocator state.
- `BusyHandler`: pager-invoked busy callback state.
- `FuncDef`, `FuncDestructor`, `FuncDefHash`: SQL function definitions, aggregate/finalizer callbacks, collations-needed flag, destructor reference counting, and hash-chain layout.
- `Savepoint`: transaction savepoint list and deferred-constraint counter snapshot.
- `Module` and `VTable`: virtual table module registrations and per-connection virtual table handles.
- `Column`, `Table`, `Index`, `IndexSample`, `FKey`, and `KeyInfo`: schema objects used to map SQL definitions to B-tree roots, column affinity/collation, index key layouts, FK actions, ANALYZE samples, and record comparison behavior.

The connection flags define behavior toggles and test controls, including column naming, count rows, writable schema, omitted read locks, full fsync/checkpoint fsync, recovery mode, reverse order, recursive triggers, foreign keys, automatic indexes, preference to built-ins, and loadable extension enablement.

### Parse Tree, Planner, and Codegen Structures

The chunk defines parser and planner state used later by expression analysis and VDBE code generation:

- `Token`: lexer slice.
- `AggInfo`: aggregate-function and aggregate-column bookkeeping, including sorting-index use and accumulator registers.
- `Expr`: expression-tree nodes with token/int payloads, child pointers, function/list/select union, collation, cursor/column/register info, aggregate info, table pointer, and optional height tracking.
- `Expr` flags such as `EP_Agg`, `EP_Resolved`, `EP_Error`, `EP_Distinct`, `EP_VarSelect`, `EP_ExpCollate`, `EP_IntValue`, `EP_xIsSelect`, `EP_Reduced`, `EP_TokenOnly`, and `EP_Static`.
- `ExprList`, `ExprSpan`, and `IdList`: lists of expressions, spanned parse fragments, and identifier lists.
- `SrcList`: FROM clauses or target table references, including database/table/alias names, subquery pointer, join metadata, cursor number, ON/USING clauses, column-use bitmask, and `INDEXED BY` binding.
- Join type flags `JT_INNER`, `JT_CROSS`, `JT_NATURAL`, `JT_LEFT`, `JT_RIGHT`, `JT_OUTER`, and `JT_ERROR`.
- `WherePlan`, `WhereLevel`, and `WhereInfo`: selected lookup strategy, nested-loop VDBE addresses, IN-loop state, virtual-table index info, one-pass flags, and output cardinality estimates.
- `NameContext`: nested name-resolution scope with FROM sources, result aliases, aggregate allowance, aggregate info, and recursion depth.
- `Select` and `SelectDest`: SELECT tree representation and result disposition (`SRT_Output`, `SRT_Table`, `SRT_EphemTab`, `SRT_Set`, `SRT_Union`, `SRT_Except`, `SRT_Coroutine`, etc.).
- `AutoincInfo`: per-autoincrement-table codegen state.
- `Trigger`, `TriggerStep`, `TriggerPrg`: trigger metadata, program-step lists, generated subprogram cache, conflict policy, and old/new column masks.
- `Parse`: the main parser/codegen context, including VDBE pointer, temp registers, cursor and memory counters, schema cookie verification, write masks, trigger state, query-loop estimates, bind variable bookkeeping, virtual table declaration state, zombie table list, and EXPLAIN select IDs.
- `DbFixer`, `StrAccum`, `InitData`, `Walker`, and walk return codes for tree rewriting, string accumulation, schema initialization callbacks, and parse-tree traversal.

## Control Flow and Data Flow

This chunk defines the skeleton used by later implementation sections:

1. SQL text is tokenized into `Token` values whose numeric kinds are defined in `parse.h`.
2. The Lemon parser builds `Expr`, `ExprList`, `SrcList`, `Select`, `Table`, `Index`, `Trigger`, and related objects inside a `Parse` context.
3. Name resolution uses nested `NameContext` objects and records resolved columns in `Expr.iTable`, `Expr.iColumn`, `Expr.pTab`, and aggregate fields.
4. Code generation emits `VdbeOp` instructions using `sqlite3VdbeAddOp*` and edits operands with `sqlite3VdbeChangeP*`.
5. The VDBE runs opcodes against `VdbeCursor` objects, `Mem` registers, `Btree` cursors, and the pager/page-cache stack.
6. Persistent pages move through `Pager` and `PCache`; dirty pages, journals, savepoints, WAL checkpoints, and page-size/file-format metadata are all exposed through the declared APIs.
7. Schema changes update `Schema` hash tables, database cookies, B-tree metadata, and eventually `sqlite_master`/`sqlite_temp_master`.

No full algorithm implementations appear in most of this chunk; it is mostly declarations and data model. The implementations begin with `global.c`, `ctime.c`, and the start of `status.c`/`vdbeInt.h`.

## State and Persistence Behavior

Important stateful and persistent surfaces in this chunk include:

- `SQLITE_FILE_HEADER "FoundationDB100"` changes the on-disk database header string from stock SQLite, making file compatibility an explicit integration contract.
- `Db.inTrans`, `sqlite3.autoCommit`, savepoint fields, deferred FK counters, and VDBE statement fields coordinate transaction state.
- `Schema.schema_cookie`, `Schema.file_format`, `Schema.enc`, `Db.pSchema`, and B-tree metadata indices (`BTREE_SCHEMA_VERSION`, `BTREE_FILE_FORMAT`, etc.) describe persistent schema state.
- `Pager` journal modes, savepoints, WAL open/close/checkpoint functions, sync configuration, locking mode, and journal-size limits are the persistence safety layer exposed to later code.
- `PgHdr` flags track dirty/needs-sync/needs-read/do-not-write pages, and `PGHDR_ZERO_COPY` adds a special page ownership/release path.
- `sqlite3PendingByte` defaults to `0x40000000`; comments state changing it creates incompatible database files and undefined behavior while operating.
- `sqlite3Config` is writable-static global configuration unless `SQLITE_OMIT_WSD` is enabled. It stores memory, mutex, page-cache, scratch, lookaside, shared-cache, init-state, and logging hooks.
- `sqlite3GlobalFunctions` is the process-global function registry, initialized once then treated as read-only.
- `sqlite3UpperToLower`, `sqlite3CtypeMap`, `sqlite3OpcodeProperty`, and `sqlite3IntTokens` are global constant lookup tables used by lexer, expression, and VDBE machinery.

## Dependencies and Integration Points

Internal subsystem dependencies visible here:

- `sqliteInt.h` is the hub: it includes limits, hash, parser token definitions, B-tree, VDBE, pager, page cache, OS, and mutex declarations.
- `Btree` depends on `Pager` for page persistence and on `BtCursor`/`KeyInfo`/`UnpackedRecord` for logical table/index access.
- `Pager` depends on `sqlite3_vfs` and `sqlite3_file` for platform I/O and on `DbPage`/`PgHdr` for cache/page ownership.
- `PCache` depends on pager callbacks for stress/dirty page cleaning.
- `Vdbe` depends on parser/codegen structures, B-tree cursors, `Mem`, functions, collations, virtual table modules, and transaction state.
- Virtual table support integrates through `sqlite3_module`, `sqlite3_vtab`, `sqlite3_vtab_cursor`, `sqlite3_index_info`, and VDBE virtual table opcodes.
- Optional features are compiled in or out via macros: WAL, shared cache, virtual tables, triggers, foreign keys, authorization, load extensions, column metadata, floating point, memory management, unlock notify, and tests.
- The compile-option diagnostics API (`sqlite3_compileoption_used`, `sqlite3_compileoption_get`) exposes selected build macros to callers unless `SQLITE_OMIT_COMPILEOPTION_DIAGS` is defined. For this build it can report items such as `THREADSAFE=0`, `OMIT_SHARED_CACHE`, and `TEMP_STORE=...` when those macros are present.

FoundationDB-specific integration signals:

- The file header and zero-copy page flag suggest a custom storage/VFS compatibility layer elsewhere in the repository.
- The non-threadsafe build and omitted shared cache reduce SQLite internal synchronization cost, presumably relying on external scheduling/serialization in FoundationDB's usage.
- The memory-status FIXME is a known performance-observability tradeoff.

## APIs and Functions Declared in This Chunk

The chunk declares many private APIs. The most important groups are:

- Memory: `sqlite3MallocInit`, `sqlite3Malloc`, `sqlite3DbMallocZero`, `sqlite3DbMallocRaw`, `sqlite3DbRealloc`, `sqlite3DbFree`, scratch/page allocators, heap pressure, benign malloc hooks, and memdebug type tracking.
- Parsing and schema: `sqlite3RunParser`, `sqlite3FinishCoding`, `sqlite3BeginParse`, `sqlite3Init`, `sqlite3InitCallback`, `sqlite3ReadSchema`, table/index/view/trigger creation and deletion APIs, `sqlite3Pragma`, `sqlite3NestedParse`.
- Expressions: `sqlite3ExprAlloc`, `sqlite3Expr`, `sqlite3PExpr`, `sqlite3ExprFunction`, `sqlite3ExprDelete`, duplication, affinity, collation, constant/null/integer checks, codegen, conditional jumps, and aggregate analysis.
- DML and query planning: `sqlite3Insert`, `sqlite3DeleteFrom`, `sqlite3Update`, `sqlite3Select`, `sqlite3WhereBegin`, `sqlite3WhereEnd`, `sqlite3GenerateConstraintChecks`, `sqlite3CompleteInsertion`, row/index delete and key generation helpers.
- Transactions: `sqlite3BeginTransaction`, `sqlite3CommitTransaction`, `sqlite3RollbackTransaction`, `sqlite3Savepoint`, `sqlite3CloseSavepoints`, `sqlite3RollbackAll`.
- Foreign keys/triggers/virtual tables: `sqlite3FkCheck`, `sqlite3FkActions`, `sqlite3Vtab*` APIs, `sqlite3CodeRowTrigger`, `sqlite3TriggerColmask`, and no-op macro replacements under omit flags.
- Utility: varint encode/decode, UTF-8 helpers, numeric conversion, string accumulation, error reporting, busy-handler invocation, schema/index lookup, compile-option diagnostics, backup update/restart, parser allocation/free/drive APIs.

## Runtime Structures in the `status.c` / `vdbeInt.h` Opening

The last part of the chunk enters `status.c` and includes private VDBE runtime definitions:

- `VdbeCursor`: VM cursor state over a B-tree or virtual table. It tracks cursor type, table/index flags, rowid validity, deferred seeks, pseudo-table register, key info, sequence counter, seek result, and a cached record header (`aType`, `aOffset`, `aRow`, `payloadSize`, `cacheStatus`).
- `VdbeFrame`: saved VM execution frame for trigger subprograms or `OP_Program`. It snapshots parent op array, memory cells, cursors, program counter, rowid/change counters, and parent frame link. Frame memory is embedded after the aligned `VdbeFrame` header.
- `Mem`: the core SQL value cell. It may hold NULL, string, integer, real, blob, rowset, frame, aggregate context, zero-blob count, encodings, destructor policy, malloc buffer, and debug shallow-copy tracking.
- `VdbeFunc`: wraps a `FuncDef` with per-argument auxdata destructors for `sqlite3_get_auxdata()` / `sqlite3_set_auxdata()` behavior.
- `sqlite3_context`: SQL function callback context containing the function definition, auxdata wrapper, return `Mem`, aggregate `Mem`, error code, and collation.
- `Vdbe`: complete statement state including program opcodes, registers, arguments, result columns, cursors, bindings, program counter, return code, error action, explain/read-only/expired flags, statement journal state, FK counters, SQL text, debug trace, trigger frames, variable invalidation mask, and linked subprograms.

These declarations are critical for later `sqlite3_step()` behavior: opcode execution mutates `Vdbe.aMem`, `Vdbe.apCsr`, `Vdbe.pc`, `Vdbe.rc`, transaction counters, and frame stacks while reading/writing B-tree pages through the pager.

## Risks and Edge Cases

- The `SQLITE_FILE_HEADER` change makes this SQLite build incompatible with default SQLite database files unless surrounding code intentionally handles the custom header.
- `SQLITE_THREADSAFE=0` and `SQLITE_MUTEX_OMIT` remove SQLite's internal mutex protection. Any accidental cross-thread use of a connection, global config, pager, or shared structures can become undefined behavior.
- `SQLITE_OMIT_SHARED_CACHE=1` compiles shared-cache locks and enter/leave calls away. Code paths that assume shared-cache semantics must be disabled or externally guarded.
- `SQLITE_DEFAULT_MEMSTATUS=0` suppresses default memory-status tracking. This can hide memory accounting details while improving performance.
- Page-size and pending-byte constants are on-disk compatibility boundaries. The comments explicitly warn that changing `PENDING_BYTE` creates incompatible files and undefined behavior.
- `PGHDR_ZERO_COPY` adds an ownership constraint: pages read through zero-copy I/O must be released through the matching VFS method. Bugs here risk leaks, use-after-release, or stale page contents.
- Many structures use flexible trailing arrays (`a[1]`, `aCol[1]`, `aColl[1]`, `apAux[1]`). Allocation size calculations must be exact.
- `Expr` supports reduced/token-only allocation forms. Accessing fields beyond the allocated prefix when `EP_Reduced` or `EP_TokenOnly` is set is explicitly unsafe.
- `VdbeOp.p4` ownership is encoded by negative `P4_*` constants. Mismatches can leak memory, double-free dynamic strings/key info, or retain ephemeral pointers.
- `Mem` string/blob ownership is encoded with flags (`MEM_Dyn`, `MEM_Static`, `MEM_Ephem`, `MEM_Term`, `MEM_Zero`). Incorrect flag transitions in later code can corrupt SQL values.
- The parser limits and VM op limits are compile-time values; raising them affects memory layout choices such as `ynVar` width and expression tree depth handling.
- Compile-option diagnostics rely on a manually sorted conditional array. Build flags not listed here are not visible through `sqlite3_compileoption_*`.

## Test Signals

Useful validation signals for this chunk and the surrounding amalgamation include:

- Compile the amalgamation with the repository's intended flags and confirm the top-level forced macros produce expected diagnostics.
- Call `sqlite3_compileoption_used("THREADSAFE")`, `sqlite3_compileoption_used("OMIT_SHARED_CACHE")`, and `sqlite3_compileoption_get()` in a smoke test when compile-option diagnostics are enabled.
- Verify that new database files created by this build use the `FoundationDB100` header and that stock SQLite files are rejected or converted only through intentional compatibility code.
- Exercise page-cache paths that set or observe `PGHDR_ZERO_COPY`, especially error, eviction, dirty-page, and release paths in the VFS integration.
- Run SQL parser/codegen smoke tests covering tokens and opcodes declared here: simple SELECT, INSERT/UPDATE/DELETE, transactions, savepoints, triggers, foreign keys, virtual tables if enabled, and WAL/checkpoint if enabled.
- Stress lookaside allocation and `Mem` ownership transitions with strings, blobs, zeroblobs, aggregate functions, user functions with auxdata, and malloc failure injection.
- Test expression-reduction paths under debug builds to catch invalid access beyond reduced/token-only `Expr` sizes.
- Run single-thread and accidental concurrent-access tests around the FoundationDB embedding boundary to confirm external serialization is effective for this `SQLITE_THREADSAFE=0` build.
- Confirm schema-cookie and file-format behavior using CREATE/DROP/ALTER, attached databases, temp databases, autovacuum, and savepoints.

## Unresolved Cross-Chunk References

This chunk mostly declares APIs. Implementations are expected later in the amalgamation:

- B-tree, pager, page-cache, OS/VFS, WAL, and journal behavior are declared here but implemented in later chunks.
- Parser actions, expression codegen, query planning, and VDBE opcode execution are declared here but implemented later.
- `sqlite3_status()` implementation begins after this chunk; only its include of `vdbeInt.h` and early private VDBE data structures are visible here.
- FoundationDB-specific behavior behind `SQLITE_FILE_HEADER`, `PGHDR_ZERO_COPY`, and any custom VFS/file-control methods must be reconciled with later source chunks.

### subset-b-008407: lines 6111-14968

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 6111-14968

## Scope And Purpose

This chunk covers a broad utility band of the SQLite amalgamation used by the FoundationDB SQLite integration. It starts with VDBE/internal declarations, then implements process and connection status reporting, SQL date/time functions, OS/VFS wrapper dispatch, malloc-fault hooks, low-level memory allocators, mutex implementations, high-level allocation wrappers, SQLite's printf/string-accumulator layer, PRNG support, UTF conversion, numeric/string utility routines, varint encoding, safety checks, overflow-safe arithmetic, and the beginning of generic hash-table support.

Most of the code is shared infrastructure rather than FoundationDB-specific storage-engine logic. It defines the behavior that higher SQLite layers rely on for memory pressure, OOM propagation, date/time SQL functions, VFS integration, encoding conversion, portable locking, diagnostic formatting, and low-level record/key encodings.

## Important APIs, Types, And Functions

Status accounting is centered on `sqlite3StatType sqlite3Stat`, `sqlite3StatusValue`, `sqlite3StatusAdd`, `sqlite3StatusSet`, public `sqlite3_status`, and public `sqlite3_db_status`. Global status tracks current and high-water values for `SQLITE_STATUS_*` counters. Database status reports lookaside usage/hits/misses, pager-cache memory, schema memory, and prepared statement memory.

Date/time support is centered on `DateTime`, whose canonical value is `iJD`, a Julian-day number scaled by milliseconds. `getDigits`, `parseTimezone`, `parseHhMmSs`, `parseYyyyMmDd`, `parseDateOrTime`, `computeJD`, `computeYMD`, `computeHMS`, `localtimeOffset`, and `parseModifier` parse and transform date values. SQL entry points include `juliandayFunc`, `datetimeFunc`, `timeFunc`, `dateFunc`, `strftimeFunc`, and the current-time wrappers, registered by `sqlite3RegisterDateTimeFunctions`.

The OS abstraction layer provides thin wrappers around `sqlite3_file` and `sqlite3_vfs` methods: `sqlite3OsRead`, `sqlite3OsWrite`, `sqlite3OsSync`, `sqlite3OsLock`, `sqlite3OsShmMap`, `sqlite3OsOpen`, `sqlite3OsDelete`, `sqlite3OsAccess`, `sqlite3OsFullPathname`, dynamic-library wrappers, randomness/sleep/current-time wrappers, `sqlite3OsOpenMalloc`, `sqlite3OsCloseFree`, and `sqlite3OsInit`. VFS registry state is held in `vfsList` and manipulated through `sqlite3_vfs_find`, `sqlite3_vfs_register`, and `sqlite3_vfs_unregister`.

Memory allocator implementations appear in several layers. `mem0.c` supplies the zero-malloc placeholder. `mem1.c` supplies the system `malloc` backend with an 8-byte size header. `mem2.c` supplies the debug allocator with guard words, backtraces, type tags, titles, and allocation histograms. `mem3.c` supplies a fixed-pool coalescing allocator with small free lists, hash free lists, a master chunk, and `sqlite3MemGetMemsys3`. `mem5.c` supplies a fixed-pool buddy allocator with power-of-two buckets and `sqlite3MemGetMemsys5`.

The high-level allocation layer in `malloc.c` is the main allocator integration point for the rest of SQLite. Important functions include `sqlite3_release_memory`, `sqlite3_soft_heap_limit64`, `sqlite3MallocInit`, `sqlite3MallocEnd`, `sqlite3_memory_used`, `sqlite3_memory_highwater`, `mallocWithAlarm`, `sqlite3Malloc`, `sqlite3_malloc`, scratch allocator functions, `sqlite3_free`, `sqlite3DbFree`, `sqlite3Realloc`, `sqlite3_realloc`, `sqlite3DbMallocRaw`, `sqlite3DbRealloc`, string duplication helpers, `sqlite3SetString`, and `sqlite3ApiExit`.

Mutex support is split into dispatch glue and platform implementations. `sqlite3MutexInit` chooses configured/default methods, `sqlite3MutexEnd` shuts them down, and public/private wrappers call `xMutexAlloc`, `xMutexEnter`, `xMutexTry`, `xMutexLeave`, and debug held/not-held checks. Implementations include no-op/debug mutexes, OS/2 mutexes, pthread mutexes with optional homegrown recursive support, and Win32 critical-section mutexes.

Formatting and string accumulation use `StrAccum` plus `sqlite3VXPrintf`. The format table supports standard conversions and SQLite internal conversions such as `%q`, `%Q`, `%w`, `%T`, `%S`, and `%r`. `sqlite3StrAccumAppend`, `sqlite3StrAccumFinish`, `sqlite3StrAccumReset`, `sqlite3VMPrintf`, `sqlite3MPrintf`, `sqlite3MAppendf`, public `sqlite3_mprintf`/`sqlite3_vmprintf`, `sqlite3_snprintf`, and `sqlite3_log` are built on top.

Randomness uses a process-global RC4-style PRNG in `sqlite3PrngType`, initialized from the current default VFS randomness method. Public `sqlite3_randomness` serializes access with `SQLITE_MUTEX_STATIC_PRNG`; test-only helpers save, restore, or reset PRNG state.

UTF and utility code includes `sqlite3Utf8Read`, UTF-8/UTF-16 read/write macros, `sqlite3VdbeMemTranslate`, `sqlite3VdbeMemHandleBom`, `sqlite3Utf8CharLen`, `sqlite3Utf16to8`, optional `sqlite3Utf8to16`, and `sqlite3Utf16ByteLen`. General utilities include `sqlite3IsNaN`, `sqlite3Strlen30`, `sqlite3Error`, `sqlite3ErrorMsg`, `sqlite3Dequote`, `sqlite3StrICmp`, public `sqlite3_strnicmp`, `sqlite3AtoF`, `sqlite3Atoi64`, `sqlite3GetInt32`, `sqlite3Atoi`, varint readers/writers, big-endian 4-byte helpers, BLOB literal decoding, connection safety checks, and overflow-checked integer arithmetic.

Hash-table support begins with `sqlite3HashInit`, `sqlite3HashClear`, `strHash`, and the start of `insertElement`. This chunk does not include the full hash insert/find/remove implementation.

## Control Flow

Status flow is simple counter mutation. Internal users call `sqlite3StatusAdd` or `sqlite3StatusSet` while holding the appropriate mutex. Public `sqlite3_status` validates the operation index, returns current and high-water values, and optionally resets the high-water mark to the current value. `sqlite3_db_status` enters the connection mutex and dispatches by status opcode. Some opcodes read lookaside counters directly; cache usage enters all btrees and sums pager memory; schema and statement usage use `db->pnBytesFreed` to run existing delete walkers in accounting mode instead of actually freeing objects.

Date/time flow starts in `isDate`. With no arguments it reads current VFS time. Numeric arguments are interpreted as Julian days. Text arguments are parsed as `YYYY-MM-DD`, `HH:MM[:SS[.FFF]]`, `now`, or a floating Julian day. Modifiers are then applied in order. They can shift by fixed day/hour/minute/second increments, perform calendar month/year arithmetic, snap to start of day/month/year, move to a weekday, convert Unix epoch seconds, or adjust between UTC and local time. Output functions compute the needed representation and return SQLite scalar results.

VFS flow is intentionally shallow. File wrappers call the active `sqlite3_io_methods` methods after optional malloc-failure test injection. VFS wrappers call the active `sqlite3_vfs` methods and normalize a few cases, such as masking open flags before `xOpen`, falling back from `xCurrentTimeInt64` to `xCurrentTime`, and allocating `sqlite3_file` storage around `xOpen` in `sqlite3OsOpenMalloc`. The registry is a mutex-protected linked list where the head is the default VFS.

Allocator initialization begins with `sqlite3MallocInit`. If no allocator is configured, `sqlite3MemSetDefault` installs the compile-time default. The wrapper initializes `mem0`, chooses the static memory mutex, partitions configured scratch memory into a freelist, validates page-cache memory configuration, then invokes the selected allocator's `xInit`. Runtime allocation through `sqlite3Malloc` rejects nonpositive and near-`INT_MAX` sizes, optionally enters the memory mutex, triggers soft-heap alarms, calls the selected `xMalloc`, and updates status counters. Public `sqlite3_malloc` autoinitializes SQLite first.

Connection-local allocation flows through `sqlite3DbMallocRaw`. If a database handle has a sticky `mallocFailed` flag, allocation fails immediately. If lookaside is enabled and the request fits, a slot is popped from the connection lookaside freelist and counters are updated. Otherwise the global allocator is used. Failure sets `db->mallocFailed`. `sqlite3ApiExit` is the final API boundary step that turns a sticky allocation failure into `SQLITE_NOMEM`, resets the flag, and applies the connection error mask.

Scratch allocation tries the configured scratch freelist first, then falls back to heap allocation and records scratch overflow bytes. `sqlite3ScratchFree` distinguishes configured scratch-memory addresses from heap fallback memory and updates the appropriate counters.

`memsys3` allocation first checks exact-size free lists, then carves from the end of the master chunk, then tries to release memory and coalesce all free chunks to rebuild a large master. Freeing marks a chunk as free, links it, and attempts to expand the master by coalescing adjacent free neighbors. `memsys5` allocation rounds to a power-of-two bucket, finds or splits a larger free block, records fragmentation/statistics, and returns an indexed pool address. Freeing marks the block free and repeatedly merges with its buddy when possible.

Mutex flow depends on compile-time and runtime thread-safety settings. `sqlite3MutexInit` installs default mutex methods if the application did not configure custom methods before initialization. With core mutexes disabled, SQLite uses no-op mutex methods. With platform mutexes enabled, dynamic mutexes are allocated per call for `SQLITE_MUTEX_FAST`/`RECURSIVE`, while static mutex ids map to process-global static mutex objects.

`sqlite3VXPrintf` scans the format string, parses flags/width/precision/length modifiers, finds a conversion entry, renders into a stack buffer or an allocated escape buffer, and appends into `StrAccum`. `StrAccum` either writes into a fixed buffer, grows with database-aware allocation, or grows with public `sqlite3_realloc`, while tracking `tooBig` and `mallocFailed`.

UTF conversion flow validates that `Mem` contains text in a non-target encoding, uses in-place byte swapping for UTF-16LE/UTF-16BE conversion, otherwise allocates a maximum-sized output buffer, transcodes character by character, releases old dynamic state, and installs the new dynamic buffer. BOM handling makes the `Mem` writeable, removes the BOM, terminates the string, and updates `Mem.enc`.

Utility parsers and encoders are performance-critical shared paths. `sqlite3AtoF` handles signs, decimal/exponent parts, whitespace, UTF-16 byte stepping, and decimal scaling. `sqlite3Atoi64` skips leading zeroes, accumulates into unsigned 64-bit state, and uses `compare2pow63` for the 19-digit boundary case. Varint writers emit 1-9 byte encodings; varint readers unroll common 1-, 2-, and 3-byte cases and fall back to full 64-bit decoding for larger 32-bit varints.

## State And Persistence Behavior

This chunk maintains process-global mutable state but does not directly persist database pages. Important global state includes `sqlite3Stat`, `vfsList`, benign malloc hooks, allocator globals (`mem0`, debug `mem`, `mem3`, `mem5`), mutex static objects, and `sqlite3Prng`. These states affect persistence indirectly because they govern allocation success, VFS selection, file I/O dispatch, thread safety, current-time values, and random rowid/temp-name generation.

Database-connection state is touched through `sqlite3_db_status` and the allocation wrappers. Lookaside freelists, lookaside counters, `db->mallocFailed`, `db->pnBytesFreed`, connection error state, schema hash tables, pager memory accounting, and prepared statement accounting all participate in this range. The `pnBytesFreed` accounting mode is particularly subtle: existing object-deletion routines are reused to estimate memory without actually freeing schema or statement structures.

Date/time functions are pure with respect to database contents, but they depend on `db->pVfs` for `now` and current-time functions. Results can become persistent if used in SQL defaults, generated values, triggers, or application writes.

Allocator state is long-lived after `sqlite3_initialize`. Fixed-pool allocators cannot change heap size after initialization. `memsys3` and `memsys5` store allocation metadata inside the configured heap block, so heap corruption or incorrect pointer classification can cascade into allocator state damage. High-water memory counters persist until reset through status APIs.

The VFS list persists for the life of the process unless changed by `sqlite3_vfs_register` or `sqlite3_vfs_unregister`. The list order defines the default VFS, so registering a new default changes future database opens and current-time/randomness providers.

The PRNG state persists across calls and is shared by all threads. Test builds can snapshot or reset it for deterministic behavior. It is seeded from the default VFS once at first use.

UTF conversion mutates `Mem` objects by releasing previous external/dynamic content and replacing encoding, flags, length, and ownership fields. These transformations affect VDBE value handling, collation, comparison, SQL function arguments, and text storage conversion paths.

## Dependencies And Integration Points

This code depends on the SQLite global configuration object, mutex subsystem, VFS subsystem, pager/btree/schema/VDBE types, `sqlite3_value` and `sqlite3_context` APIs, and compile-time feature macros. Many functions are compiled conditionally based on `SQLITE_OMIT_DATETIME_FUNCS`, `SQLITE_OMIT_LOCALTIME`, `SQLITE_OMIT_UTF16`, `SQLITE_MEMDEBUG`, `SQLITE_ENABLE_MEMSYS3`, `SQLITE_ENABLE_MEMSYS5`, platform mutex macros, and test/debug macros.

The status layer integrates with memory wrappers, scratch allocation, lookaside allocation, pager cache accounting, schema hash tables, and VDBE statement lists. The memory wrappers update `SQLITE_STATUS_MEMORY_USED`, `SQLITE_STATUS_MALLOC_SIZE`, `SQLITE_STATUS_MALLOC_COUNT`, `SQLITE_STATUS_SCRATCH_USED`, `SQLITE_STATUS_SCRATCH_SIZE`, and `SQLITE_STATUS_SCRATCH_OVERFLOW`.

Date/time functions integrate with the SQL function registry via `FuncDefHash` and `sqlite3FuncDefInsert`. They depend on VFS current-time methods, `sqlite3_value_*` conversion APIs, `sqlite3_result_*` APIs, the SQLite formatter, and local-time C library functions guarded by mutexes when thread-safe alternatives are unavailable.

The OS wrapper layer is the bridge between pager/btree code and `sqlite3_vfs`/`sqlite3_io_methods`. WAL/shared-memory methods (`xShmMap`, `xShmLock`, `xShmBarrier`, `xShmUnmap`) are routed here, so this range is on the path for journal and WAL coordination even though it does not implement the platform filesystem itself.

The allocator backend layer integrates with `sqlite3_config(SQLITE_CONFIG_MALLOC)` and fixed heap configuration. The high-level allocator layer integrates with soft heap limits, memory-management builds through `sqlite3PcacheReleaseMemory`, lookaside slots, scratch memory, memory debugging type tags, and API error translation.

Mutex implementations integrate with OS/2 APIs, pthreads, or Win32 critical sections, depending on the build. They are also used by static SQLite locks such as `SQLITE_MUTEX_STATIC_MASTER`, `STATIC_MEM`, and `STATIC_PRNG`.

Formatting integrates with parser/debug internals through internal-only `%T` and `%S` conversions and SQL string construction through `%q`, `%Q`, and `%w`. Logging uses this same formatter but deliberately avoids dynamic allocation because it can run while allocator mutexes are held.

UTF conversion integrates with VDBE `Mem` ownership functions such as `sqlite3VdbeMemMakeWriteable`, `sqlite3VdbeMemRelease`, `sqlite3VdbeMemSetStr`, and `sqlite3VdbeChangeEncoding`. Numeric and varint utilities integrate with SQL literal parsing, record encoding, btree cell parsing, rowid handling, and on-disk format logic.

The hash-table start integrates with SQLite schema and function hash tables. The case-folding hash uses `sqlite3UpperToLower`, matching case-insensitive symbol behavior elsewhere in SQLite.

## Risks And Edge Cases

The status API assumes aligned 32-bit reads/writes are atomic. On targets where that is false, `sqlite3_status` is not thread-safe. `sqlite3_db_status` relies on connection mutex discipline and uses delete functions for memory accounting, so changes to those delete routines must preserve `db->pnBytesFreed` behavior.

Date/time parsing deliberately supports a limited 4-digit year range for formatted dates and uses the proleptic Gregorian calendar. Local-time conversion clamps years outside 1971-2037 to year 2000 before asking the C library, which avoids `time_t` range issues but means historical/future local offsets are approximated. Fractional month/year modifiers use fixed 30-day and 365-day approximations for fractional parts. The timezone parser treats `Z` as valid but only sets `validTZ` when the offset is nonzero, so zero-offset handling relies on already-canonical input.

`strftimeFunc` precomputes a maximum output length and enforces `SQLITE_LIMIT_LENGTH`, but format additions must update both the sizing loop and rendering loop. Unknown `%` conversions return NULL rather than a string error.

VFS wrappers trust method tables to be valid. Some wrappers, such as shared-memory calls, do not check whether optional methods are NULL in this range. `sqlite3OsCurrentTimeInt64` fallback multiplies a double Julian day by milliseconds, so precision depends on the VFS `xCurrentTime` implementation when `xCurrentTimeInt64` is absent.

Memory allocation has several subtle failure modes. The public wrappers intentionally reject sizes near `INT_MAX` to avoid backend integer overflow. `sqlite3DbMallocRaw` depends on the sticky `db->mallocFailed` rule: once one allocation fails, later connection-local allocations must fail until the API boundary resets the flag. Code that bypasses this wrapper can break assumptions in callers that allocate multiple dependent objects.

Lookaside classification is address-range based, so connection lookaside ranges must not overlap unrelated heap memory. Scratch allocation checks whether a freed pointer lies between `pScratch` and `pScratchEnd`; invalid frees could corrupt the scratch freelist.

`memsys3` and `memsys5` store metadata adjacent to or inside the fixed heap. Off-by-one writes in clients can corrupt freelists, block sizes, or buddy control bytes. `memsys3` coalescing and master-chunk logic rely heavily on header bits for current/previous checkout state. `memsys5` requires power-of-two atom sizing and accurate `aCtrl` metadata. Both allocators are high risk under memory corruption and should be stress-tested under OOM and fragmentation.

The debug allocator is intentionally intrusive. It always reallocates by allocating a new block, fills memory with pseudo-random bytes, asserts guard words, and tracks type tags. That is useful for tests but can expose timing or layout assumptions hidden under the system allocator.

Mutex correctness is build-dependent. No-op mutexes are only suitable when SQLite is not used concurrently. The pthread homegrown recursive path assumes atomic `pthread_equal` and coherent memory. Win32 `sqlite3_mutex_try` is compiled to always return `SQLITE_BUSY` in this version, which is valid for SQLite's use but can surprise external users expecting an actual try-lock optimization.

`sqlite3_log` cannot allocate and uses a fixed stack buffer. Long formatted log messages are truncated through the non-growing `StrAccum` path. Formatter internal conversions are gated by `useExtended`; exposing internal format strings through public APIs would return early or omit expected output.

The PRNG is explicitly not cryptographic. It is adequate for SQLite rowid/temp-name style usage in this version, but it should not be reused for secrets. Its initialization depends on the current default VFS randomness method.

UTF conversion accepts some non-strict UTF-8 encodings while mapping surrogates and noncharacters to replacement values. Behavior around invalid byte sequences is intentionally SQLite-specific and may differ from strict Unicode libraries. BOM handling mutates buffers and requires writeability; allocation failure must leave values in a consistent state.

Integer conversion and varint routines are boundary-sensitive. `sqlite3Atoi64` distinguishes positive `9223372036854775808` overflow from negative minimum-int acceptance. Varint readers are unrolled and depend on byte availability supplied by callers; corrupt database input reaches fallback paths but still assumes safe buffer bounds from higher btree/pager validation.

This chunk ends in the middle of hash-table insertion support. Any per-file final report should merge this partial hash coverage with the following chunk before drawing conclusions about complete hash behavior.

## Test Signals

Relevant status tests should cover valid and invalid `sqlite3_status` opcodes, high-water reset behavior, lookaside hit/miss counters, cache-used accounting across attached btrees, and schema/statement memory accounting with `db->pnBytesFreed`.

Date/time test signals include parsing of `now`, Julian-day floats, numeric arguments, timezone suffixes, `T` separators, leap/day boundary cases, `unixepoch`, `weekday N`, `start of` modifiers, fractional seconds, fractional months/years, localtime/UTC conversion, omitted full datetime support, and `strftime` length-limit failures.

VFS tests should verify method dispatch, open-flag masking, `xCurrentTimeInt64` fallback, VFS registry ordering/default selection, unregister behavior, and malloc-failure injection under `SQLITE_TEST`.

Allocator tests should exercise `sqlite3_malloc`/`free`/`realloc`, soft heap limits, memory high-water reset, scratch pool vs heap overflow, lookaside allocation/miss paths, sticky `mallocFailed`, `sqlite3ApiExit`, zero-size and overlarge allocations, and OOM callback behavior. For `memsys3` and `memsys5`, fragmentation, coalescing, split/merge, realloc growth, fixed-heap initialization failure, and dump/debug assertions are the important signals.

Mutex tests should cover configured mutex methods, no-op/debug held assertions, dynamic vs static mutex ids, recursive acquisition, try-lock return codes, and platform initialization/shutdown paths where available.

Formatter tests should include standard integer/float/string conversions, SQLite SQL-escaping conversions `%q`, `%Q`, `%w`, internal `%T`/`%S` when allowed, width/precision limits, dynamic string `%z` ownership, `sqlite3_snprintf` non-growing truncation, mprintf OOM, and log formatting with no allocation.

Randomness tests in built-in test builds can use save/restore/reset state to verify deterministic replay. Runtime tests should verify output length, mutex serialization, and reseeding after reset.

UTF and utility tests should cover UTF-8/UTF-16 round trips, byte-order swapping, BOM stripping, malformed UTF-8 replacement behavior, character length counts, UTF-16 byte counts over surrogate pairs, NaN handling, dequoting, case-insensitive comparisons, floating and integer boundary parsing, varint encode/decode for 1-9 byte values, four-byte big-endian helpers, BLOB literal decoding, safety-check logging paths, and checked 64-bit arithmetic overflow.

Hash tests for this chunk alone can only validate initialization, clearing, and case-folding hash behavior. Full insertion/removal/find behavior requires the continuation chunk.

### subset-b-008408: lines 14969-22849

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 14969-22849

## Scope And Purpose

This chunk spans several independent pieces of the vendored SQLite amalgamation used under FoundationDB's `contrib/sqlite` tree. It begins in the tail of `hash.c`, covers the generated opcode-name table, includes the full OS/2 VFS implementation, and then covers most of the Unix VFS implementation through the beginning of Mac OS X proxy-locking conch acquisition.

The largest behavioral surface is the VFS layer. The OS/2 section maps SQLite's `sqlite3_vfs` and `sqlite3_io_methods` contracts onto `Dos*` APIs, including path-codepage conversion, byte-range locking, dynamic extension loading, randomness, sleep, and current-time methods. The Unix section implements file open/read/write/sync/truncate/delete/access, POSIX advisory locking, alternative locking styles, WAL shared-memory mapping, filesystem-specific method selection, temporary-file naming, and the first half of proxy-lock support.

The chunk is source-tree-aligned to the amalgamation rather than a final per-file report. It stops mid-function inside `proxyConchLock()`, so proxy-lock control flow after stale-conch breaking must be reconciled by the following chunk.

## Important APIs, Types, And Functions

The hash-table tail exposes `sqlite3HashFind()` and `sqlite3HashInsert()` over the internal `Hash`, `HashElem`, and `_ht` bucket structures. The local helpers `rehash()`, `findElementGivenHash()`, and `removeElementGivenHash()` resize buckets, locate case-insensitive string keys, update the doubly linked insertion list, and clear the table when the last element is removed.

`sqlite3OpcodeName()` is a debug/explain/profile helper generated from opcode metadata. It returns the string name for VDBE opcodes such as `Goto`, `Column`, `Transaction`, `OpenRead`, `ResultRow`, and virtual-table opcodes when explain/debug support is compiled in.

The OS-common include contributes diagnostics and test hooks shared by OS backends: `OSTRACE`, optional `sqlite3Hwtime()` performance timing, simulated I/O and disk-full failure counters (`sqlite3_io_error_pending`, `sqlite3_diskfull_pending`, etc.), and `sqlite3_open_file_count`.

The OS/2 VFS uses `os2File`, a `sqlite3_file` subclass containing an OS/2 `HFILE`, optional delete-on-close path, and current SQLite lock level. Its main file methods are `os2Close`, `os2Read`, `os2Write`, `os2Truncate`, `os2Sync`, `os2FileSize`, `os2Lock`, `os2Unlock`, `os2CheckReservedLock`, `os2FileControl`, `os2SectorSize`, and `os2DeviceCharacteristics`.

OS/2 path and VFS helpers include `initUconvObjects()`, `freeUconvObjects()`, `convertUtf8PathToCp()`, `convertCpPathToUtf8()`, `getTempname()`, `os2FullPathname()`, `os2Open()`, `os2Delete()`, `os2Access()`, `os2DlOpen()`/`os2DlSym()`/`os2DlClose()`, `os2Randomness()`, `os2Sleep()`, `os2CurrentTime()`, `os2CurrentTimeInt64()`, `sqlite3_os_init()`, and `sqlite3_os_end()`.

The Unix VFS defines `unixFile`, `UnixUnusedFd`, `unixFileId`, `unixInodeInfo`, `unixShmNode`, and `unixShm`. `unixFile` stores the file descriptor, directory descriptor, lock state, inode lock object, last errno, lock-specific context, WAL shared-memory handle, chunk-size hint, cached filesystem flags, and debug transaction-counter tracking state. `unixInodeInfo` is the process-local coordination object that prevents POSIX locks from being accidentally dropped by another file descriptor in the same process.

The Unix system-call override table `aSyscall[]` provides VFS-level test injection for `open`, `close`, `access`, `getcwd`, `stat`, `fstat`, `ftruncate`, `fcntl`, `read`, `pread`, `write`, `pwrite`, `fchmod`, and optional `posix_fallocate`. It is managed through `unixSetSystemCall()`, `unixGetSystemCall()`, and `unixNextSystemCall()`.

Unix file I/O methods include `unixRead()`, `unixWrite()`, `unixSync()`, `unixTruncate()`, `unixFileSize()`, `unixFileControl()`, `unixSectorSize()`, and `unixDeviceCharacteristics()`. Lower-level wrappers such as `robust_open()`, `robust_close()`, `robust_ftruncate()`, `seekAndRead()`, `seekAndWrite()`, `full_fsync()`, and `unixLogErrorAtLine()` centralize EINTR handling, close semantics, fsync behavior, and error logging.

The locking backends in this range include:

- POSIX byte-range locking: `findInodeInfo()`, `unixCheckReservedLock()`, `unixFileLock()`, `unixLock()`, `posixUnlock()`, `unixUnlock()`, and `unixClose()`.
- No-op locking: `nolockCheckReservedLock()`, `nolockLock()`, `nolockUnlock()`, and `nolockClose()`.
- Dot-file locking: `dotlockCheckReservedLock()`, `dotlockLock()`, `dotlockUnlock()`, and `dotlockClose()`.
- `flock()` locking when enabled: `flockCheckReservedLock()`, `flockLock()`, `flockUnlock()`, and `flockClose()`.
- VxWorks semaphore locking when enabled: `semCheckReservedLock()`, `semLock()`, `semUnlock()`, and `semClose()`.
- Apple AFP locking when enabled: `afpSetLock()`, `afpCheckReservedLock()`, `afpLock()`, `afpUnlock()`, and `afpClose()`.
- Apple NFS special unlock handling through `nfsUnlock()`, which delegates to `posixUnlock()` with the NFS workaround enabled.

WAL shared-memory support, compiled when WAL is not omitted, is implemented by `unixOpenSharedMemory()`, `unixShmSystemLock()`, `unixShmPurge()`, `unixShmMap()`, `unixShmLock()`, `unixShmBarrier()`, and `unixShmUnmap()`.

Method dispatch is built by the `IOMETHODS` macro, which creates `sqlite3_io_methods` tables and finder functions for `posix`, `nolock`, `dotlock`, `flock`, `sem`, `afp`, `proxy`, and `nfs` styles as applicable. `autolockIoFinderImpl()` chooses lock methods by filesystem type and lock support on Apple and VxWorks builds.

Unix VFS-level entry points covered here include `fillInUnixFile()`, `openDirectory()`, `unixTempFileDir()`, `unixGetTempname()`, `findReusableFd()`, `findCreateFileMode()`, `unixOpen()`, `unixDelete()`, `unixAccess()`, `unixFullPathname()`, dynamic loader wrappers, `unixRandomness()`, `unixSleep()`, `unixCurrentTimeInt64()`, `unixCurrentTime()`, and `unixGetLastError()`.

The proxy-locking portion begins with `proxyLockingContext`, `proxyGetLockPath()`, `proxyCreateLockPath()`, `proxyCreateUnixFile()`, `proxyGetHostID()`, `proxyBreakConchLock()`, and the first part of `proxyConchLock()`.

## Control Flow

Hash lookup computes a case-insensitive string hash modulo the current bucket count when buckets exist, then calls `findElementGivenHash()`. Without buckets, lookup scans the single linked list. Insertion first searches for an existing key. A non-null `data` replaces existing data or allocates a new `HashElem`; a null `data` removes the matching element. Once the table reaches at least 10 entries and more than twice the current bucket count, `rehash()` allocates a larger benign-malloc bucket array and reinserts all existing elements.

The OS/2 open path validates SQLite open flags, creates a temp filename when `zName` is null, translates the UTF-8 filename into the active OS/2 codepage, computes `DosOpen()` action and sharing modes, and falls back from read/write to read-only if needed. Delete-on-close stores a converted absolute path so `os2Close()` can force-delete it after closing the handle. Reads and writes seek with `DosSetFilePtr()` and call `DosRead()`/`DosWrite()`, with short reads zero-filling the unread buffer.

OS/2 locking raises the file's lock state through SQLite's standard sequence: `NO_LOCK -> SHARED_LOCK -> RESERVED_LOCK/PENDING_LOCK -> EXCLUSIVE_LOCK`. Shared locks use the SQLite shared lock range, reserved/pending/exclusive locks use fixed bytes, and unlock collapses state back to `NO_LOCK` or `SHARED_LOCK` depending on the request. `os2CheckReservedLock()` probes whether a reserved lock is held by this or another process.

Unix initialization starts with compile-time feature selection: large-file flags, optional locking styles, VxWorks handling, WAL mmap support, and Apple filesystem APIs. It defines a `unixFile` object for all Unix-family VFSes and a system-call dispatch table so tests can override kernel calls without replacing the whole VFS.

POSIX lock acquisition in `unixLock()` is process-aware. It enters the global Unix mutex, checks `unixInodeInfo` to see whether another handle in the same process already holds an incompatible lock, then performs the minimal `fcntl(F_SETLK)` transitions. A shared lock first takes a temporary lock on `PENDING_BYTE`, then locks one or all bytes in the shared range and releases pending. Reserved locks take `RESERVED_BYTE`. Exclusive locks take a pending lock and then write-lock the full shared range. If exclusive acquisition fails after pending is held, the file remains at `PENDING_LOCK`.

Unlocking in `posixUnlock()` downgrades higher locks to shared or no-lock. It has a special Apple/NFS path that clears and reestablishes parts of the shared range to work around lockd behavior. When the last process-local shared lock is released, it clears the OS lock and closes any file descriptors deferred in `unixInodeInfo.pUnused`.

`unixClose()` first unlocks the file, then avoids directly closing a descriptor if doing so would drop POSIX locks still held by another connection on the same inode. Such descriptors are put on the inode's pending-unused list and are either reused by `findReusableFd()` during a later open of the same database or closed when the last lock is gone.

Alternative Unix lock backends flatten or adapt the same SQLite lock states. No-op locking only updates no state and is intended for read-only or externally synchronized use. Dot-file locking creates and deletes a `*.lock` file, mapping all lock levels to an exclusive lock. `flock()` and VxWorks semaphores also collapse all held states into a single exclusive OS-level lock while tracking SQLite's intermediate levels in memory. AFP locking uses `fsctl()` byte-range locks, with a randomly selected shared byte and a full shared range for exclusive locking.

Unix reads and writes are offset-based through `pread`/`pwrite` or seek plus `read`/`write`. `unixRead()` returns `SQLITE_IOERR_SHORT_READ` after zero-filling missing bytes. `unixWrite()` loops until the requested write completes or an error/full condition occurs, and debug builds track whether writes changed the database transaction counter. `unixSync()` calls `full_fsync()` on the file and, for newly created journal/WAL/master-journal files, fsyncs and closes the parent directory descriptor once.

WAL shared memory opens lazily on first `unixShmMap()`. `unixOpenSharedMemory()` reuses one `unixShmNode` per inode in the process, creates or opens the `-shm` file next to the database unless the `unix-excl` process lock makes heap-backed memory sufficient, truncates stale shm files if it can take the dead-man switch, and links a per-connection `unixShm`. `unixShmMap()` extends and mmaps regions on demand. `unixShmLock()` enforces local sibling conflicts with bitmasks before taking or releasing fcntl locks on the shm file. `unixShmUnmap()` unlinks the connection, decrements the node reference count, optionally deletes the shm file, and purges mmap regions and the descriptor when the last connection closes.

`unixOpen()` is the main `sqlite3_vfs.xOpen` path. It validates flag combinations, optionally reuses a deferred database file descriptor, creates a temporary name for anonymous temp files, computes POSIX open flags and permissions, falls back to read-only when read/write open fails, unlinks delete-on-close files, opens a directory descriptor for created journal/WAL files that need directory sync, marks close-on-exec, detects MS-DOS filesystems for Apple workarounds, optionally transforms non-local files into proxy-locking files, and finally calls `fillInUnixFile()`.

`fillInUnixFile()` selects a locking method from the VFS `pAppData` finder, initializes inode state for locking styles that need it, allocates lock-specific contexts for dotlock and AFP, opens VxWorks semaphores when needed, stores read-only/exclusive flags, sets the final `sqlite3_io_methods`, and increments the open-file test counter. Error paths close descriptors carefully and release allocated locking context.

The proxy-locking setup builds a local lock-proxy path from either `LOCKPROXYDIR`, Darwin's user temp directory, or `/tmp`, creates missing lock directories, opens helper `unixFile` objects for conch or lock files, and obtains a host UUID. `proxyBreakConchLock()` tries to replace a stale conch file by copying it through a sibling `-break` file and renaming it back. `proxyConchLock()` then attempts a conch lock, waits 0.5 seconds after the first busy result, verifies the conch modification time and host id on the second busy result, waits 10 seconds, and on the third attempt may break a stale lock. The chunk ends before this function's final return path.

## State And Persistence Behavior

The hash table owns `HashElem` allocations and the bucket array, but it does not copy key strings. `sqlite3HashInsert()` stores the caller's `pKey` pointer directly and only replaces the stored key pointer when replacing data for an existing key. Callers must keep key storage valid for the lifetime of the hash entry.

OS/2 file state is mostly volatile inside `os2File`, but it mutates persistent filesystem state through writes, truncates, syncs, deletes, and byte-range locks. Delete-on-close persists only until `os2Close()`, where the saved path is force-deleted. Temporary names are generated under `sqlite3_temp_directory`, `TEMP`, `TMP`, `TMPDIR`, or the current drive.

Unix persistent state includes database, journal, WAL, shm, temp, dot-lock, proxy-lock, and conch files. Database file bytes are changed by `unixWrite()` and `unixTruncate()`, while durability is controlled by `unixSync()` and directory syncs. Delete operations optionally sync the containing directory to make journal removal durable.

Unix lock state is split between OS-level locks and in-process metadata. `unixInodeInfo.eFileLock`, `nShared`, `nLock`, `bProcessLock`, and `pUnused` model the effective lock state for all `unixFile` handles in the process that refer to the same inode. This state is guarded by SQLite's static master mutex and is not persisted. OS-level locks are byte-range locks on the database or shm file, `flock()` locks, semaphores, dot-lock files, AFP byte locks, or proxy helper locks depending on method.

The WAL shared-memory file is persistent filesystem state but is treated as rebuildable coordination data. If no other process holds the dead-man switch, a newly opened `unixShmNode` truncates the shm file to zero. In `unix-excl` mode, no shm file is created and the regions are heap allocations attached to the single-process inode state.

Open-file reuse is process-local state. A descriptor that cannot be closed safely due to POSIX lock semantics is detached from a closing `unixFile`, stored on `unixInodeInfo.pUnused`, and later reused only when the path resolves to the same device/inode and the flags match.

File creation modes preserve database-adjacent permissions. Temporary delete-on-close files are `0600`; database and master-journal files use `SQLITE_DEFAULT_FILE_PERMISSIONS`; WAL and main-journal files try to copy permissions from the corresponding database file.

Proxy locking persists two helper files. The conch file lives beside the database and records a version byte, host id, and proxy lock path. The proxy lock file lives in a local lock directory and is used as the target of normal SQLite advisory locks after the conch says this host owns proxy access. This range includes path creation and stale-conch breaking but not the full proxy acquisition/update workflow.

## Dependencies And Integration Points

The VFS code is the lower boundary used by the pager through `sqlite3Os*` wrappers. The pager depends on this chunk for file descriptors, byte-accurate reads and writes, sync semantics, file-size queries, truncation, open flags, deletion, access checks, randomness, sleep, current time, dynamic extension loading, WAL shared-memory methods, and lock-state transitions.

The lock constants (`NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`, `PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, and `SHARED_SIZE`) are shared with pager locking rules. Correct pager behavior assumes the VFS implements the documented transition order and returns `SQLITE_BUSY` rather than hard I/O errors for normal lock contention.

Testing integrates through `SQLITE_TEST` globals for simulated I/O errors, disk-full errors, fake current time, sync counts, open-file counts, and host-id perturbation for proxy locking. The Unix system-call override API is another key integration point for fault injection and sandboxing.

Platform dependencies are extensive. OS/2 depends on `DosOpen`, `DosRead`, `DosWrite`, `DosSetFileLocks`, `DosQueryPathInfo`, `DosLoadModule`, ULS conversion APIs, and OS/2 time/randomness sources. Unix depends on POSIX file APIs, optional `pread`/`pwrite`, `mmap`, `fcntl`, `fsync`/`fdatasync`, `dlopen`, `gettimeofday`, `statfs`, `flock`, VxWorks semaphores, Apple `fsctl`, Darwin temp-directory and host-UUID APIs, and compile-time macros controlling availability.

The method-finder design integrates with `sqlite3_vfs.pAppData`: VFS objects store a pointer to a finder-function pointer, not the function pointer directly, to satisfy C90 restrictions on casting `void *` to a function pointer. `fillInUnixFile()` relies on that convention.

WAL integration depends on `sqlite3_io_methods.iVersion == 2` for POSIX methods with shared-memory callbacks. Locking styles that do not support shared memory use method version 1 and null out WAL shm methods through the generated table.

FoundationDB integration in this chunk is indirect. This is a vendored SQLite OS layer without explicit FoundationDB calls. Its correctness still affects FoundationDB's SQLite-backed storage behavior because all pager durability, lock coordination, WAL shared memory, and fault-injection behavior flows through these VFS methods.

## Risks And Edge Cases

The Unix POSIX lock workaround is fragile by design. Closing any descriptor for an inode can release process-owned POSIX locks, so `unixClose()`, `findReusableFd()`, `releaseInodeInfo()`, and `closePendingFds()` must remain consistent. A missed reference count or premature close can silently drop locks held by other SQLite connections in the same process.

Network filesystem behavior is a major risk. Dot-file, AFP, NFS, flock, no-op, and proxy styles all trade off correctness and concurrency differently. Autodetection depends on `statfs()` results and probing `fcntl()`. A wrong choice can cause database corruption, poor concurrency, or severe performance loss.

The no-op lock style is intentionally unsafe for multiple writers. It is appropriate only for read-only databases or when external synchronization is guaranteed. Any path that accidentally selects `nolockIoMethods` for a writable shared database is high risk.

WAL shared memory depends on all processes using the same shm path and compatible build flags. `SQLITE_SHM_DIRECTORY` can redirect shm files away from the database directory; comments state this is unsupported and incompatible across builds because two processes may then coordinate through different shm files.

`unixShmLock()` maintains both process-local lock masks and OS locks. Bugs in sibling-mask conflict detection can permit incompatible locks in one process even if OS-level locks would not catch them. Conversely, failure to release system locks when the last local holder unlocks can wedge WAL access.

Short-read semantics are deliberate. Both OS/2 and Unix zero-fill unread portions and return `SQLITE_IOERR_SHORT_READ`. Pager callers must treat this as a recoverable condition in cases where reading beyond EOF is expected.

`unixSync()` ignores directory fsync failures in some cases by design, based on historical filesystem behavior. This reduces false failures but weakens the diagnostic signal for filesystems where directory sync really is required for crash durability.

The Apple MS-DOS filesystem workaround in `findInodeInfo()` writes one byte to zero-size files so that inode numbers become stable. `unixFileSize()` then reports size 0 when the actual size is 1. This is subtle cross-layer state; changes can affect empty-database open behavior.

Compile-gated paths deserve direct scrutiny. In the `HAVE_POSIX_FALLOCATE` branch, the shown amalgamation contains suspicious code in `fcntlSizeHint()` (`pFile->.h` and assignment-like `errno=EINTR`) and the `osFallocate` macro text is malformed-looking. These may be hidden on builds without `HAVE_POSIX_FALLOCATE`, but enabling that feature should be compile-tested.

`unixNextSystemCall()` appears to iterate using `aSyscall[0]` instead of `aSyscall[i]` in the loop body. That would make system-call enumeration return the first entry repeatedly rather than the next live syscall, reducing the usefulness of the VFS override introspection API.

`proxyCreateUnixFile()` allocates `pUnused` before some error returns. The `fd<0` branch that returns `SQLITE_BUSY`, `SQLITE_PERM`, `SQLITE_IOERR_LOCK`, or `SQLITE_CANTOPEN_BKPT` should be checked for leaks of that allocation in the compiled proxy-lock path.

`proxyBreakConchLock()` reports directly to `stderr`. That is unusual in a library VFS path and can surprise embedders. It also relies on atomic-enough rename semantics and on the conch contents being long enough and version-compatible.

The chunk ends inside `proxyConchLock()`. Any conclusion about full proxy-lock correctness, conch upgrade/downgrade persistence, and proxy method close/unlock behavior requires the next chunk.

## Test Signals

Hash-table tests should cover case-insensitive key lookup, insertion without key copying, replacement returning old data, deletion by inserting null data, resizing under benign malloc failure, and clearing after the final removal.

OS/2 coverage, if the platform is supported, should exercise read/write/truncate/sync/file-size operations, short-read zero fill, lock escalation and unlock, reserved-lock probing, delete-on-close, UTF-8 to codepage path conversion, temp-file naming, dynamic extension loading, randomness, fake current time, and simulated I/O/disk-full errors.

Unix file-I/O tests should cover read-only fallback, exclusive create with `O_NOFOLLOW`, temp-file creation, delete-on-close unlinking, directory fsync for journals and WAL files, short reads, partial writes, disk-full simulation, chunk-size and size-hint behavior, file-size after truncation, access checks treating zero-size files as non-existent for existence checks, and full path resolution after current-directory errors.

Locking tests should cover POSIX same-process multiple connections on hard links or symlinks to the same inode, shared-to-reserved-to-exclusive transitions, failed exclusive leaving pending state, downgrade to shared, close with outstanding locks, reuse of deferred descriptors, and lock conflict translation from errno to `SQLITE_BUSY` or I/O codes.

Alternative locking tests should exercise dot-lock stale files, `flock()` contention, VxWorks semaphore contention if available, AFP shared-byte selection and reserved-lock tracking, NFS downgrade behavior, read-only filesystem autoselection, and explicit `unix-none`/external-synchronization scenarios.

WAL tests should cover shm file creation and truncation under the dead-man switch, mapping region 0 without extension, extending to later regions, heap-backed shared memory under `unix-excl`, shared and exclusive shm locks across sibling connections, unmap with and without delete, and recovery from mmap/ftruncate/open failures.

System-call override tests should call `xSetSystemCall`, `xGetSystemCall`, and `xNextSystemCall`, inject failing `open`, `fcntl`, `ftruncate`, `pread`, `pwrite`, and `close` behavior, and verify `lastErrno` and SQLite result-code mapping.

Proxy-lock tests for Apple builds should cover `:auto:` path generation, lock directory creation, helper `unixFile` creation, read-only fallback, simulated alternate host IDs, stale conch break decisions, conch modification-time races, and allocation cleanup on open failures. Full proxy-lock tests need the following chunk as well.

Portability build tests should compile this amalgamation with combinations of `SQLITE_OS_OS2`, `SQLITE_OS_UNIX`, `SQLITE_ENABLE_LOCKING_STYLE`, `SQLITE_OMIT_WAL`, `OS_VXWORKS`, `__APPLE__`, `HAVE_POSIX_FALLOCATE`, `USE_PREAD`, `USE_PREAD64`, `SQLITE_NO_SYNC`, and `SQLITE_TEST` to expose compile-gated branches that normal Linux builds skip.

### subset-b-008409: lines 22850-30612

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 22850-30612

## Scope And Purpose

This chunk covers a broad storage and platform slice of the SQLite amalgamation vendored under FoundationDB. It starts at the end of the MacOS proxy-locking implementation in `os_unix.c`, then includes the Windows VFS implementation in `os_win.c`, the sparse bitmap implementation in `bitvec.c`, the pager-facing page-cache wrapper in `pcache.c`, the default page-cache backend in `pcache1.c`, the rowid set container in `rowset.c`, and the opening definitions of `pager.c`.

The first half is operating-system adaptation. Unix proxy locking coordinates AFP/NFS-style lock proxy files through a conch file, while the Windows VFS implements file handles, WinCE lock emulation, byte-range database locks, WAL shared-memory mapping, path conversion, deletion/access/full-path helpers, dynamic library loading, randomness, sleep, time, and VFS registration.

The middle of the chunk implements memory-resident data structures used by the pager and btree layers. `Bitvec` tracks journaled or savepoint-protected page numbers using bitmap, hash, or recursive sub-bitmaps. `PCache` wraps the pluggable `sqlite3_pcache` interface and maintains dirty-page ordering and pager stress callbacks. `pcache1` is the default cache backend with hash lookup, global or per-cache LRU groups, optional `SQLITE_CONFIG_PAGECACHE` static slots, cache-size enforcement, recycling, and memory-pressure handling. `RowSet` stores rowids with cheap appends, batch-aware membership tests, and sorted extraction.

The final section enters the pager. It declares the WAL interface, documents rollback-journal invariants and pager state transitions, defines the `Pager` and `PagerSavepoint` structures, and begins journal-header helpers. This is the conceptual foundation for SQLite's atomic commit, rollback, savepoint, WAL, and file-locking behavior implemented in later pager code.

## Important APIs, Types, And Functions

The proxy-locking functions are MacOS-specific and compiled under `defined(__APPLE__) && SQLITE_ENABLE_LOCKING_STYLE`. `proxyTakeConch()` is the core coordinator: it obtains the host id, locks and reads the conch file, compares host id and lock-proxy path, creates or rewrites the conch contents when needed, reopens the database descriptor, creates the local proxy lock file, and marks `proxyLockingContext.conchHeld`. `proxyReleaseConch()` releases the conch lock. `proxyCreateConchPathname()` derives `.<db>-conch` beside the database. `switchLockProxyPath()` replaces the proxy path only while unlocked. `proxyTransformUnixFile()` converts an existing `unixFile` to proxy locking by allocating a `proxyLockingContext`, opening the conch file, preserving the old context and I/O methods, and installing `proxyIoMethods`. `proxyFileControl()` handles `SQLITE_GET_LOCKPROXYFILE` and `SQLITE_SET_LOCKPROXYFILE`. `proxyCheckReservedLock()`, `proxyLock()`, `proxyUnlock()`, and `proxyClose()` delegate actual locking and cleanup through the proxy lock file after taking the conch.

The Unix `sqlite3_os_init()` in this span registers the unix VFS family with `UNIXVFS`: `unix`, `unix-none`, `unix-dotfile`, `unix-excl`, and conditionally `unix-namedsem`, `unix-posix`, `unix-flock`, `unix-afp`, `unix-nfs`, and `unix-proxy`. `sqlite3_os_end()` is a no-op for Unix.

`os_common.h` contributes debug and test hooks shared by OS layers. `OSTRACE` depends on `sqlite3OSTrace` in debug builds. The optional `sqlite3Hwtime()` implementations provide low-level cycle counters for performance tracing. `SimulateIOError`, `SimulateDiskfullError`, `sqlite3_io_error_*`, `sqlite3_diskfull_*`, and `OpenCounter()` are test instrumentation used throughout the VFS methods.

`winFile` is the Windows `sqlite3_file` subclass. It stores the VFS pointer, Windows file handle, current SQLite lock level, chosen shared-lock byte for Win9x, last Windows error, sector size, WAL shared-memory handle, path, and configured chunk size. Under WinCE it also stores delete-on-close state plus named mutex/shared-memory lock state.

Windows filename conversion helpers include `utf8ToUnicode()`, `unicodeToUtf8()`, `mbcsToUnicode()`, `unicodeToMbcs()`, public `sqlite3_win32_mbcs_to_utf8()`, and `utf8ToMbcs()`. `isNT()` caches whether the process is running a WinNT-class API environment, with a test override through `sqlite3_os_type`.

WinCE-specific helpers emulate file locking using a named mutex plus mapped shared state. `winceCreateLock()` creates the mutex and file mapping derived from the database path. `winceDestroyLock()` releases local lock contributions from shared state. `winceLockFile()`, `winceUnlockFile()`, and `winceLockFileEx()` implement the subset of byte-range locking SQLite requires.

The Windows `sqlite3_io_methods` vector `winIoMethod` points to `winClose()`, `winRead()`, `winWrite()`, `winTruncate()`, `winSync()`, `winFileSize()`, `winLock()`, `winUnlock()`, `winCheckReservedLock()`, `winFileControl()`, `winSectorSize()`, `winDeviceCharacteristics()`, and WAL shared-memory methods. `seekWinFile()` is the common 64-bit seek wrapper over `SetFilePointer()`. `getReadLock()` and `unlockReadLock()` isolate shared-lock acquisition differences between WinNT and legacy Windows.

The Windows WAL shared-memory layer defines `winShmNode` for a process-local shared-memory file and mapped regions, and `winShm` for each connection using that node. `winOpenSharedMemory()` opens or reuses `<db>-shm`, initializes the deadman switch, and links a connection. `winShmLock()` implements SQLite shared-memory lock masks over Windows byte locks, coordinating sibling connections in-process before taking system locks. `winShmMap()` extends and maps WAL-index regions with allocation-granularity alignment. `winShmUnmap()`, `winShmPurge()`, `winShmBarrier()`, and `winShmSystemLock()` close mappings, delete backing storage when requested, provide a mutex-based memory barrier, and wrap `LockFileEx`/`UnlockFileEx`.

Windows VFS methods include `winOpen()`, `winDelete()`, `winAccess()`, `winFullPathname()`, `getSectorSize()`, `winDlOpen()`, `winDlError()`, `winDlSym()`, `winDlClose()`, `winRandomness()`, `winSleep()`, `winCurrentTimeInt64()`, `winCurrentTime()`, and `winGetLastError()`. Windows `sqlite3_os_init()` registers the `win32` VFS and initializes `winSysInfo.dwAllocationGranularity` for WAL mapping.

`Bitvec` is a fixed-size 512-byte object with three internal representations: `u.aBitmap[]` for small bit ranges, `u.aHash[]` for sparse larger ranges, and recursive `u.apSub[]` sub-bitmaps once the hash table becomes too full. Public functions are `sqlite3BitvecCreate()`, `sqlite3BitvecTest()`, `sqlite3BitvecSet()`, `sqlite3BitvecClear()`, `sqlite3BitvecDestroy()`, `sqlite3BitvecSize()`, and test-only `sqlite3BitvecBuiltinTest()`.

`PCache` is the pager-side cache object. It tracks dirty pages in LRU order (`pDirty`, `pDirtyTail`, `pSynced`), reference count, configured cache size, page and extra sizes, purgeability, stress callback, pluggable cache handle, and cached page 1. Key functions are `sqlite3PcacheInitialize()`, `sqlite3PcacheShutdown()`, `sqlite3PcacheOpen()`, `sqlite3PcacheSetPageSize()`, `sqlite3PcacheFetch()`, `sqlite3PcacheRelease()`, `sqlite3PcacheRef()`, `sqlite3PcacheDrop()`, `sqlite3PcacheMakeDirty()`, `sqlite3PcacheMakeClean()`, `sqlite3PcacheCleanAll()`, `sqlite3PcacheClearSyncFlags()`, `sqlite3PcacheMove()`, `sqlite3PcacheTruncate()`, `sqlite3PcacheClose()`, `sqlite3PcacheDirtyList()`, and cache-size/refcount/pagecount accessors.

`pcache1` implements the default `sqlite3_pcache_methods`. `PGroup` represents either a per-cache or global LRU/recycling group. `PCache1` owns one hash table of page keys to `PgHdr1` entries. `pcache1_g` stores global cache configuration, optional static page slots, and under-pressure state. Public or installed entry points include `sqlite3PCacheBufferSetup()`, `sqlite3PageMalloc()`, `sqlite3PageFree()`, `sqlite3PCacheSetDefault()`, and, under memory-management builds, `sqlite3PcacheReleaseMemory()`. Internal methods `pcache1Fetch()`, `pcache1Unpin()`, `pcache1Rekey()`, `pcache1Truncate()`, and `pcache1Destroy()` make up the default backend.

`RowSet` stores `RowSetEntry` nodes allocated from `RowSetChunk` blocks. `sqlite3RowSetInit()` constructs a rowset in caller-provided memory, `sqlite3RowSetClear()` frees chunks, `sqlite3RowSetInsert()` appends rowids, `sqlite3RowSetNext()` returns rowids in sorted order, and `sqlite3RowSetTest()` performs batch-aware membership checks. Helpers `rowSetMerge()`, `rowSetSort()`, `rowSetTreeToList()`, `rowSetNDeepTree()`, `rowSetListToTree()`, and `rowSetToList()` convert between append lists, sorted lists, and balanced-ish binary trees.

The pager opening section declares WAL APIs such as `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalBeginReadTransaction()`, `sqlite3WalRead()`, `sqlite3WalBeginWriteTransaction()`, `sqlite3WalFrames()`, `sqlite3WalCheckpoint()`, and savepoint helpers. It defines pager states `PAGER_OPEN`, `PAGER_READER`, `PAGER_WRITER_LOCKED`, `PAGER_WRITER_CACHEMOD`, `PAGER_WRITER_DBMOD`, `PAGER_WRITER_FINISHED`, and `PAGER_ERROR`, plus `UNKNOWN_LOCK`, codec macros, `MAX_SECTOR_SIZE`, `PagerSavepoint`, and the full `Pager` struct. Early pager helpers include `pagerUseWal()`, debug-only `assert_pager_state()` and `print_pager_state()`, `subjRequiresPage()`, `pageInJournal()`, `read32bits()`, `write32bits()`, `pagerUnlockDb()`, `pagerLockDb()`, atomic-write `jrnlBufferSize()`, page-hash debug helpers, `readMasterJournal()`, `journalHdrOffset()`, `zeroJournalHdr()`, and `writeJournalHdr()`.

## Control Flow

Proxy locking begins by transforming an already opened Unix file with `proxyTransformUnixFile()`. The routine derives the database path, opens or prepares the conch file, stores the old lock context and I/O method table, and installs `proxyIoMethods`. Later lock operations first call `proxyTakeConch()`. That function obtains a shared conch lock, reads the conch, decides whether the host id and proxy path match, upgrades to exclusive locking if the conch must be rewritten, writes the conch version/host/path payload, optionally matches permissions to the database file, reopens the database descriptor, creates the actual proxy lock file, and only then marks the conch as held. Subsequent `proxyLock()` and `proxyUnlock()` simply delegate to the proxy file and mirror the proxy lock level back onto the real database `unixFile`.

Windows ordinary I/O follows the `sqlite3_file` method table. `winOpen()` validates SQLite open-flag combinations, creates a temp name if `zName` is null, converts UTF-8 to wide or multibyte OS encoding, maps SQLite flags to `CreateFileW/A` access and creation modes, retries read-write opens as read-only when needed, initializes `winFile`, and under WinCE initializes emulated shared locking for main databases. Reads and writes call `seekWinFile()` before `ReadFile()` or a loop over `WriteFile()`. Truncation honors `SQLITE_FCNTL_CHUNK_SIZE` by rounding up to configured chunks. Sync delegates to `FlushFileBuffers()` unless `SQLITE_NO_SYNC` is compiled.

Windows database locking implements SQLite's standard byte-range protocol. `winLock()` refuses to lower locks, validates legal transitions, optionally grabs the pending byte, acquires a shared/read lock, reserved lock, pending state, or exclusive shared-byte range as required, then updates `winFile.locktype`. If exclusive acquisition fails after dropping a read lock, it attempts to reacquire the read lock. `winUnlock()` releases exclusive, reserved, read, and pending locks according to the target level and records the lowered locktype even though some Windows unlock calls are not surfaced as hard failures. `winCheckReservedLock()` checks the local lock state first, then probes the reserved byte remotely.

Windows WAL shared memory opens lazily from `winShmMap()`. The first map request calls `winOpenSharedMemory()`, which looks for an existing `winShmNode` by case-insensitive `-shm` filename, or creates one, opens the shm file, uses the deadman-switch byte to decide whether to truncate stale content, and links a `winShm` connection into the node's sibling list. `winShmLock()` computes a bitmask for the requested WAL lock range, uses sibling masks to avoid redundant or conflicting system locks within the process, and then acquires or releases Windows byte locks only when needed. `winShmMap()` checks file size, optionally extends it for writers, allocates or grows the mapping-region array, creates file mappings, maps views aligned to `winSysInfo.dwAllocationGranularity`, and returns a region pointer adjusted by the intra-granularity shift.

`Bitvec` starts in direct bitmap mode for small sizes. For larger sizes it inserts one-based bit numbers into an open-addressed hash table. If collisions and cardinality exceed `BITVEC_MXHASH`, `sqlite3BitvecSet()` copies the hash to stack storage, clears the union, sets `iDivisor`, and reinserts all values recursively into sub-bitmaps. `sqlite3BitvecTest()` follows the same recursive path before testing either bitmap bits or hash slots. `sqlite3BitvecClear()` either clears one bitmap bit or rebuilds the hash table without the cleared value; it does not collapse recursive representations.

`sqlite3PcacheFetch()` is the pager's cache acquisition path. It lazily creates the backend cache on first create fetch, asks the backend for a page with a create strength derived from purgeability and dirty state, and if a soft allocation fails it invokes the pager stress callback on a suitable dirty unreferenced page. It prefers a dirty page that does not require journal sync (`pSynced`) before falling back to any unreferenced dirty tail page. Once a backend page is returned, it initializes `PgHdr` fields and extra storage if needed, increments reference counts, and caches page 1 specially.

Dirty-page lifecycle in `PCache` is list-based. `sqlite3PcacheMakeDirty()` clears `PGHDR_DONT_WRITE`, sets `PGHDR_DIRTY`, and adds the page to the dirty-list head. `sqlite3PcacheRelease()` decrements references; if the page becomes unreferenced and clean it calls `pcacheUnpin()`, otherwise dirty pages are moved to the head. `sqlite3PcacheMakeClean()` removes dirty state and unpins if no references remain. `sqlite3PcacheDirtyList()` converts the dirty list to `pDirty` links and merge-sorts it by page number for pager writeback.

The default `pcache1Fetch()` flow is lookup, budget check, hash resize, recycle, allocate. It first searches `PCache1.apHash`. If absent and creation is disallowed, it returns null. For soft create requests it refuses allocation when pinned pages exceed cache or group budgets or when memory pressure is reported. It resizes the hash table if full. It may recycle the global/group LRU tail, freeing it if page sizes differ, otherwise repurposing it for the target cache. If no reusable page exists, it drops the group mutex, allocates via `pcache1AllocPage()`, then relocks and inserts the new page into the hash table. `pcache1Unpin()` either frees immediately when reuse is unlikely or over budget, or pushes the page onto the LRU head for later recycling.

`RowSet` append behavior is intentionally cheap: `sqlite3RowSetInsert()` allocates from `pFresh`, appends to the `pEntry` list through `pRight`, and tracks whether inserts remain sorted. Sorted extraction via `sqlite3RowSetNext()` first calls `rowSetToList()`, which sorts the append list if needed and merges any tree generated by membership tests. Batch membership testing via `sqlite3RowSetTest()` converts all entries inserted before a new batch into a tree, then searches only that tree; inserts made after the batch change remain invisible to tests with the same batch number until the batch changes again.

The pager code in this chunk is mostly definitions and early helpers. The documented state machine moves from `OPEN` to `READER` on shared locking, from `READER` through writer states as transactions journal and modify cache/database pages, and into `ERROR` on hard I/O conditions that can leave cache state inconsistent. `pagerLockDb()` and `pagerUnlockDb()` wrap VFS lock calls while conservatively maintaining `Pager.eLock`; the special `UNKNOWN_LOCK` value prevents a failed unlock from suppressing hot-journal recovery. `writeJournalHdr()` aligns to the next sector boundary, updates active savepoint header offsets, initializes the journal header with magic, record count placeholder, checksum seed, original database size, sector size, and page size, then writes a full header sector in page-sized chunks.

## State And Persistence Behavior

The proxy-locking conch file is durable coordination state. It stores a version byte, host id, and local proxy lock path. `proxyTakeConch()` may rewrite that file and `fsync()` it, then uses the referenced proxy lock file as the actual byte-lock target. `proxyLockingContext` holds transient state: `conchHeld`, `lockProxyPath`, `lockProxy`, `conchFile`, `dbPath`, old locking context, and old I/O methods. A `conchHeld` value below zero represents read-only filesystem lockless access.

Windows VFS state lives in `winFile` and in OS handles. `lastErrno` records Windows errors for later `SQLITE_LAST_ERRNO` and `xGetLastError` reporting. `locktype` mirrors the SQLite lock state. `szChunk` affects future truncation and size hints. On WinCE, local and shared lock state persists in named shared memory until `winceDestroyLock()` subtracts local contributions. Delete-on-close temp files are removed by Windows flags where available, or by explicit retry loops on WinCE.

Windows WAL state is split between process memory and filesystem-backed shm files. `winShmNodeList` is process-global and protected by the static master mutex. Each `winShmNode` owns the `-shm` file handle, mapped regions, sibling connection list, last error, and refcount. Mapped WAL-index regions are backed by the shm file and protected by byte locks plus in-process masks. `winShmPurge()` unmaps regions, closes handles, optionally deletes the shm file, and removes unreferenced nodes.

`Bitvec` state is purely in-memory and owned by pager/savepoint logic. It records whether page numbers have been journaled or saved. It may allocate recursive sub-bitmaps under memory pressure from large sparse sets; failures return `SQLITE_NOMEM` from set operations and must be propagated by callers that require journaling correctness.

`PCache` maintains pager-visible page state but does not itself persist pages. Dirty flags and dirty-list order determine what the pager writes and in which order. `PGHDR_NEED_SYNC` marks dirty pages whose journal records require syncing before the page may be written to the database. `pSynced` caches the newest dirty page that can be spilled without a journal sync, allowing stress eviction to preserve rollback invariants.

`pcache1` owns memory allocation and recycling state. If `SQLITE_CONFIG_PAGECACHE` is configured, page buffers are drawn from the static slot list until exhausted; overflow allocations come from `sqlite3Malloc()` and update `SQLITE_STATUS_PAGECACHE_OVERFLOW`. Purgeable pages count against `PGroup.nCurrentPage`; unpinned pages can remain in the LRU and be reassigned to other caches in the same group. Non-purgeable caches, such as in-memory databases, are not LRU-recycled the same way.

`RowSet` never persists to disk. It allocates chunks using the database connection allocator and frees them only on clear or exhaustion after `sqlite3RowSetNext()`. Its key state transition is one-way for extraction: after `SMALLEST`/`sqlite3RowSetNext()` begins, inserts are prohibited by assertion because the append list is consumed as a sorted list.

`Pager` is the major durable-state coordinator. The struct stores VFS handles for the database, main journal, and sub-journal; lock and transaction state; database size snapshots; journal offsets and header offsets; checksum seed; bitmaps for journal membership; active savepoints; backup list; page-cache handle; file names; codec callbacks; and WAL connection state. The documented invariants require that pages are only overwritten after rollback data is safe, writes are page-aligned, journal/database syncing precedes journal finalization, locks protect readers and writers, and database change-counter bytes are updated before releasing exclusive locks.

Journal headers are persistent rollback records. `writeJournalHdr()` writes magic and metadata, while `zeroJournalHdr()` finalizes persistent journals by truncating or zeroing the first 28 bytes and syncing when required. `readMasterJournal()` reads and validates a master-journal pointer appended to a journal tail using length, checksum, and magic; a checksum mismatch is treated as no valid master journal, which forces rollback safety.

## Dependencies And Integration Points

The OS-layer code integrates with SQLite's VFS and file-method contracts: `sqlite3_vfs_register()`, `sqlite3_file`, `sqlite3_io_methods`, lock constants (`SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`), `sqlite3Os*` wrappers used by pager code, and file-control opcodes such as `SQLITE_FCNTL_LOCKSTATE`, `SQLITE_LAST_ERRNO`, `SQLITE_FCNTL_CHUNK_SIZE`, `SQLITE_FCNTL_SIZE_HINT`, and proxy-lock controls.

The Windows code depends heavily on Win32 APIs: `CreateFileW/A`, `ReadFile`, `WriteFile`, `SetFilePointer`, `SetEndOfFile`, `FlushFileBuffers`, `LockFile`, `LockFileEx`, `UnlockFile`, `UnlockFileEx`, `CreateFileMapping`, `MapViewOfFile`, `UnmapViewOfFile`, `GetFileAttributes*`, `GetFullPathName*`, `GetTempPath*`, `FormatMessage*`, `LoadLibrary*`, `GetProcAddress`, `GetSystemTimeAsFileTime`, `QueryPerformanceCounter`, and `GetDiskFreeSpace*`. WinCE uses a reduced API surface and replaces byte locks with mutex/shared-memory emulation.

The WAL shared-memory VFS methods are the platform hooks consumed by the WAL module declared later in this same chunk. `sqlite3WalOpen()` and related routines expect `xShmMap`, `xShmLock`, `xShmBarrier`, and `xShmUnmap` to provide cross-process WAL-index storage and locking.

`Bitvec` is consumed by the pager and btree/pager savepoint paths. In this chunk it is referenced immediately by `PagerSavepoint.pInSavepoint`, `Pager.pInJournal`, `subjRequiresPage()`, and `pageInJournal()`. It relies on SQLite allocation helpers including `sqlite3MallocZero()`, `sqlite3StackAllocRaw()`, `sqlite3StackFree()`, and `sqlite3_free()`.

`PCache` is the bridge between pager code and the configurable `sqlite3GlobalConfig.pcache` backend. It depends on `PgHdr` flags, pager stress callbacks, global pcache methods (`xCreate`, `xFetch`, `xUnpin`, `xRekey`, `xTruncate`, `xDestroy`, `xCachesize`, `xPagecount`), and the zero-copy hook `unpinZeroCopy()` defined outside this chunk. The pager later uses this wrapper for all page acquisition, dirty tracking, spilling, refcounting, and sorted dirty writeback.

`pcache1` integrates with global SQLite configuration and status systems: `sqlite3_config(SQLITE_CONFIG_PCACHE, ...)`, `sqlite3GlobalConfig.bCoreMutex`, static mutexes `SQLITE_MUTEX_STATIC_LRU` and `SQLITE_MUTEX_STATIC_PMEM`, `sqlite3StatusSet/Add()`, `sqlite3HeapNearlyFull()`, memory-debug type tags, benign malloc scopes, and optional `SQLITE_ENABLE_MEMORY_MANAGEMENT`.

`RowSet` is a utility for higher layers that need rowid membership and sorted rowid iteration, commonly query execution and trigger/foreign-key style bookkeeping. It depends on the connection allocator (`sqlite3DbMallocRaw`, `sqlite3DbFree`) so allocation failures set the owning database's malloc-failed state.

The pager definitions integrate with all storage layers above and below: btree calls pager APIs for transactions and pages, pager calls VFS methods for files and locks, page cache supplies `PgHdr` objects, `Bitvec` records journaling coverage, WAL APIs provide log-mode behavior, codec macros support encryption/compression extensions, and debug/test macros expose counters and consistency checks.

## Risks And Edge Cases

`proxyTakeConch()` has a complex retry path for auto-generated proxy paths. A stale conch file with a matching host id but unusable lock path causes a retry with `forceNewLockPath`; mistakes in this path can leave multiple processes using different proxy lock files. The function also closes and reopens the database descriptor after taking the conch, so error handling around `robust_close()` and `robust_open()` is critical.

Proxy locking treats a read-only filesystem with no conch file as lockless by setting `conchHeld = -1`. That permits read access but depends on the filesystem truly being immutable; if the assumption is wrong, concurrency safety is lost. `proxyCheckReservedLock()` also has a suspicious assignment `pResOut=0` in the lockless branch instead of `*pResOut=0`, although the lockless branch returns success and callers may observe an unchanged output value.

Windows path conversion uses direct `malloc()` and `free()` by design. Several routines allocate based on Windows-reported character counts, so off-by-one or wide-character size mistakes can become memory safety problems. The `mbcsToUnicode()` implementation computes `nByte` as a byte count and then multiplies by `sizeof(WCHAR)` again for allocation, which overallocates rather than underallocates on normal Windows but is easy to misread.

Windows locking behavior has unavoidable ambiguity on failed unlocks and old Windows APIs. The code updates lock state optimistically in some paths and relies on retry loops for pending locks, close, and delete. Antivirus/indexer interference is explicitly handled with deletion retries, but persistent `ERROR_ACCESS_DENIED` still yields `SQLITE_IOERR_DELETE`.

The Windows WAL shm implementation matches `winShmNode` by case-insensitive filename string with a comment that a stronger file identity would be better. Hard links, path aliases, or unusual filesystem case behavior could create duplicate nodes for the same backing file or incorrectly merge different files. Mapping code must also respect allocation granularity; mistakes in offset adjustment would expose the wrong WAL-index bytes.

`winAccess(SQLITE_ACCESS_EXISTS)` treats a zero-length file as non-existent. This is SQLite-specific behavior and can surprise callers expecting raw filesystem semantics. It is important for hot-journal and database-open logic because an empty journal is not considered an existing journal to recover.

`Bitvec` uses fixed 32-bit page numbers and recursive subdivision. It assumes callers pass valid in-range values to `sqlite3BitvecSet()` and `sqlite3BitvecClear()`; some violations are only assertions. Rehashing depends on stack allocation of the old hash array and ORs together recursive set return codes, so one allocation failure during migration can leave a partially converted structure.

`PCache` correctness depends on dirty-list invariants and `PGHDR_NEED_SYNC`. If `pSynced` is stale, stress spilling may select a page that requires journal sync or fail to free memory when possible. `sqlite3PcacheMove()` reorders dirty pages with `PGHDR_NEED_SYNC` so spill ordering remains conservative after page-number changes.

`pcache1ResizeHash()` drops the PGroup mutex while allocating. It then relocks and applies the new table, but this pattern requires the caller's state to remain valid across the unlock. The design is intentional to avoid malloc under the LRU mutex, yet future changes around hash-table mutation must preserve that assumption.

The default cache backend can recycle a page from a different cache in the same group only if page sizes match. If sizes differ, it frees and allocates instead, which can cause memory churn under mixed page-size workloads. `pcache1UnderMemoryPressure()` also uses a global under-pressure flag as an optimization without always locking on read.

`RowSet` batch semantics are subtle: a test with the same batch number intentionally does not see inserts made since the last batch change. Callers that expect immediate membership visibility must change the batch number. Inserting after extraction begins is guarded by assertion rather than a runtime error.

The pager state machine is highly sensitive to I/O error placement. The `PAGER_ERROR` state exists because rollback or journal-finalization failures can make cached pages inconsistent with disk. Any later code that bypasses `pager_error`-style handling after a hard I/O failure risks returning corrupt cached content or writing it back.

`UNKNOWN_LOCK` is a conservative workaround for failed unlocks while leaving error state. If later hot-journal detection ignores this state, SQLite could mistake its own unknown exclusive lock for another process's reserved lock and skip rollback of a hot journal.

Journal finalization with `zeroJournalHdr()` must sync after zeroing or truncating unless `noSync` is set. Incorrect sync flags or size-limit truncation ordering can change crash-recovery guarantees, especially for `PAGER_JOURNALMODE_PERSIST` and master-journal transactions.

## Test Signals

Unix proxy-locking tests should cover explicit and `:auto:` proxy paths, stale conch contents, host-id matches and mismatches, read-only conch files, read-only filesystem lockless access, failed old proxy path creation with retry to a new path, permission matching after conch creation, `SQLITE_GET_LOCKPROXYFILE`, `SQLITE_SET_LOCKPROXYFILE`, and close cleanup of conch and proxy files.

Windows VFS tests should exercise read/write/truncate/sync/file-size behavior, partial read zero-fill and `SQLITE_IOERR_SHORT_READ`, chunk-size truncation rounding, read-write open fallback to read-only, delete retry behavior, access checks including zero-length files, temp-name generation, full-path conversion, sector-size fallback, dynamic extension loading, randomness byte counts, sleep rounding, time conversion, and formatted last-error reporting.

Windows locking tests should verify valid lock transitions from `NO_LOCK` through shared/reserved/exclusive, failed pending locks returning `SQLITE_BUSY`, shared-lock byte behavior on non-NT builds if still supported, reserved-lock probing while local and remote locks exist, downgrade to shared/no-lock, WinCE named mutex/shared-memory emulation, and preservation of `lastErrno`.

WAL shared-memory tests should open multiple connections in one process and across processes, verify shared and exclusive WAL locks conflict correctly, map read-only missing regions as null with `SQLITE_OK`, extend and map writer regions, unmap with and without delete, purge unreferenced nodes, recover stale shm files via the deadman switch, and exercise allocation-granularity offsets with multiple regions.

`Bitvec` tests should cover small direct bitmaps, sparse hash inserts, duplicate inserts, hash collisions, transition to recursive sub-bitmaps, clear and retest behavior, out-of-range tests returning false, null bitvec operations, allocation-failure handling, and `sqlite3BitvecBuiltinTest()` programs that deliberately introduce mismatches.

`PCache` tests should cover lazy backend creation, fetch without create, soft create under cache pressure, stress callback selection preferring non-`PGHDR_NEED_SYNC` pages, dirty-to-clean transitions, unpinning clean pages, dropping referenced pages, page-1 tracking, moving dirty pages to new page numbers, truncating with referenced page 1, sorted dirty-list output, cache-size propagation, and zero-copy unpin integration.

`pcache1` tests should exercise static pagecache slot setup and overflow allocation accounting, hash resize, LRU pin/unpin order, recycling across caches in a shared `PGroup`, separate-cache versus global-cache modes, cache-size enforcement, truncation of pinned and unpinned pages, rekeying hash entries, memory release under `SQLITE_ENABLE_MEMORY_MANAGEMENT`, and stats reporting under `SQLITE_TEST`.

`RowSet` tests should cover sorted and unsorted insert streams, duplicate removal during merge, sorted extraction order, chunk allocation failure propagation through the database connection, batch tests that see only prior batches, switching repeatedly between test batches, converting tree state back to list for extraction, and assertion-only misuse such as inserting after `sqlite3RowSetNext()`.

Pager tests for this chunk should focus on invariants and helper behavior: state assertions for each pager state, lock wrapper behavior on successful and failed VFS locks, `UNKNOWN_LOCK` hot-journal recovery paths, `subjRequiresPage()` across multiple savepoints, `pageInJournal()` with null and populated bitvecs, big-endian `read32bits()`/`write32bits()`, atomic-write buffer-size gating by device characteristics and sector size, page-hash checking under `SQLITE_CHECK_PAGES`, master-journal tail parsing with good and bad checksums, journal header alignment, zero/truncate journal finalization, and journal header contents for no-sync, memory-journal, and safe-append modes.

### subset-b-008410: lines 30613-37428

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 30613-37428

## Scope

This chunk covers the latter half of SQLite's pager implementation and the opening portion of `wal.c` inside the FoundationDB vendored SQLite amalgamation. It starts in the tail of journal-header parsing, continues through rollback-journal playback, pager open/read/write/commit/rollback/savepoint APIs, WAL mode switching, and then begins WAL file and wal-index infrastructure through iterator merge-sort setup.

The range is not a complete source-file unit. It begins after earlier pager state/type definitions and helper routines have already been declared, and it ends in the middle of WAL checkpoint iterator support after `walMergesort()`. The final per-file research should reconcile this with adjacent chunks for complete pager and WAL behavior.

## Purpose

The pager code in this chunk is the transactional storage boundary between btree pages and the VFS. It manages page-cache references, database-file locks, rollback journals, sub-journals for savepoints, hot-journal recovery, commit and rollback sequencing, change-counter maintenance, page-size/cache settings, and the transition to and from WAL mode.

The WAL code that starts near the end documents and implements the durable write-ahead log format and the transient shared-memory wal-index. It defines how WAL frames are checksummed, indexed by database page number, recovered after crashes, and opened through the VFS.

FoundationDB's copy includes a notable read-only WAL optimization in `readDbPage()`: for read-only pagers using WAL, if a page is not found in WAL, it tries `xReadZeroCopy()` on the database file and marks the page `PGHDR_ZERO_COPY`; `unpinZeroCopy()` releases it with `xReleaseZeroCopy()`. This depends on nonstandard VFS methods being available in this vendored integration.

## Important APIs, Types, and Functions

### Pager transaction and recovery helpers

- `writeMasterJournal()` appends a master-journal pointer record to the end of a rollback journal for multi-database transactions. It writes `PAGER_MJ_PGNO`, the master filename, length, checksum, and journal magic, then truncates any persistent-journal tail beyond the record so hot-journal detection can find it reliably.
- `pager_unlock()`, `pager_error()`, `pager_end_transaction()`, and `pagerUnlockAndRollback()` implement pager state cleanup. They destroy journal bitvecs and savepoints, end WAL read/write transactions, unlock or downgrade database locks, finalize rollback journals according to journal mode, and move the pager back to `PAGER_OPEN` or `PAGER_READER`.
- `pager_playback_one_page()` replays one journal or sub-journal record into the database file and/or page cache. It validates page numbers, checksums main-journal records, uses a `Bitvec` to avoid duplicate savepoint replay, handles page-1 reserve-size and file-version state, honors `PGHDR_NEED_SYNC`, and reinitializes page extra data through `xReiniter`.
- `pager_playback()` performs full rollback-journal replay, including master-journal existence checks, journal header parsing, original-size truncation, hot-journal cache reset, database sync, journal finalization, optional master-journal deletion, and sector-size restoration.
- `pagerPlaybackSavepoint()` rolls back savepoint state by replaying selected portions of the main journal and sub-journal, or delegates to WAL savepoint undo for WAL databases.

### Pager read, write, and commit APIs

- `sqlite3PagerOpen()` allocates one contiguous block containing `Pager`, `PCache`, database fd, sub-journal fd, main journal fd, and pathname buffers. It opens the database unless it is temp or memory-backed, chooses default page size from defaults, sector size, and optional atomic-write capabilities, initializes `PCache`, lock state, journal mode, sync flags, and WAL path.
- `sqlite3PagerSharedLock()` opens a read transaction. In rollback mode it obtains a shared lock, detects and rolls back hot journals, validates the cached file-version bytes at offset 24, opens WAL mode if a `-wal` file is present, and computes `dbSize`. In WAL mode it starts a WAL read transaction snapshot.
- `sqlite3PagerAcquire()`, `sqlite3PagerLookup()`, `sqlite3PagerRef()`, and `sqlite3PagerUnref()` manage page-cache references. `Acquire` either returns an existing initialized page, zero-fills out-of-range/no-content pages, or reads from WAL/database using `readDbPage()`. Releasing the last reference may trigger rollback and unlock.
- `readDbPage()` reads a page from WAL if present, otherwise from the database file. It treats short reads as zero-filled tail, updates `dbFileVers` from page 1, applies the pager codec, increments read counters, and includes the FoundationDB zero-copy read path for read-only WAL misses.
- `pager_open_journal()`, `pager_write()`, and `sqlite3PagerWrite()` start rollback-journal logging and mark pages writable. They allocate `pInJournal`, write journal headers and page records with checksums, update savepoint bitvecs, set `PGHDR_NEED_SYNC`, and handle the special case where multiple pages share a disk sector.
- `syncJournal()` upgrades to an exclusive lock, syncs or updates journal headers based on `SQLITE_IOCAP_SAFE_APPEND` and `SQLITE_IOCAP_SEQUENTIAL`, clears stale future journal headers in persistent mode, and transitions from `PAGER_WRITER_CACHEMOD` to `PAGER_WRITER_DBMOD`.
- `pager_write_pagelist()` writes dirty cache pages to the database file in page order, skipping pages beyond the current image or flagged `PGHDR_DONT_WRITE`, updating page 1 file-version bytes and backup consumers.
- `sqlite3PagerCommitPhaseOne()` implements the durable part of commit: update change counters, ensure truncation victims are journaled for auto-vacuum, write master-journal name, sync journal, write dirty pages, resize database file, and sync the database. In WAL mode it writes dirty pages as WAL frames and cleans the cache.
- `sqlite3PagerCommitPhaseTwo()` makes rollback-mode commit irrevocable by finalizing the journal using `pager_end_transaction()`. `sqlite3PagerRollback()` restores rollback-mode state with journal playback or WAL-mode state with savepoint/WAL undo.

### Pager configuration, savepoints, and integration APIs

- `sqlite3PagerSetCachesize()`, `sqlite3PagerSetSafetyLevel()`, `sqlite3PagerSetPagesize()`, `sqlite3PagerMaxPageCount()`, `sqlite3PagerReadFileheader()`, and `sqlite3PagerPagecount()` expose cache, synchronous, page-size, size-limit, header-read, and page-count controls to upper layers.
- `sqlite3PagerOpenSavepoint()` and `sqlite3PagerSavepoint()` create, release, and roll back pager savepoints. Savepoints store original database size, main-journal offsets, sub-journal record counts, per-savepoint bitvecs, and WAL savepoint data.
- `sqlite3PagerDontWrite()` optimizes pages whose contents no longer matter, typically freelist leaves, by marking dirty pages as `PGHDR_DONT_WRITE` when there are no savepoints.
- `sqlite3PagerMovepage()` supports auto-vacuum page relocation. It preserves rollback semantics by sub-journaling dirty moved pages, moves/evicts colliding cache entries, preserves `PGHDR_NEED_SYNC` hazards, and in memory databases keeps the original page available for rollback.
- `sqlite3PagerSetJournalMode()`, `sqlite3PagerLockingMode()`, `sqlite3PagerOpenWal()`, `sqlite3PagerCloseWal()`, `sqlite3PagerCheckpoint()`, and related accessors bridge btree pragmas and APIs to pager state, rollback journal deletion, WAL opening/closing, and checkpointing.
- Optional codec hooks (`sqlite3PagerSetCodec()`, `sqlite3BtreePagerSetCodec()`, `sqlite3PagerGetCodec()`, `sqlite3PagerCodec()`) transform page bytes when reading, writing journals, writing database pages, and writing WAL frames.

### WAL structures and helpers

- `WalIndexHdr` is the shared wal-index header copied twice in shared memory. It stores version, initialization flag, checksum byte order, page size, `mxFrame`, database page count, last-frame checksum, salts, and header checksum.
- `WalCkptInfo` tracks checkpoint backfill progress and per-reader read marks. `READMARK_NOT_USED` marks unused reader slots.
- `Wal` stores VFS and file handles, shared wal-index mappings, page size, lock/read-only/exclusive state, current wal-index header, WAL filename, and checkpoint sequence.
- `WalIterator` and nested `WalSegment` describe checkpoint iteration over the latest WAL frame per database page in page-number order.
- WAL constants define file format versions, locking-byte indexes, header and frame sizes, magic number, wal-index layout, hash-table sizes, and `walFrameOffset()`.
- `walIndexPage()`, `walCkptInfo()`, `walIndexHdr()`, `walHashGet()`, `walFramePage()`, and `walFramePgno()` map shared-memory wal-index pages and expose page-number arrays/hash tables.
- `walChecksumBytes()`, `walEncodeFrame()`, and `walDecodeFrame()` implement WAL header/frame checksum and frame validation using salts, page number, commit-size field, and byte-order-dependent checksum accumulation.
- `walLockShared()`, `walUnlockShared()`, `walLockExclusive()`, and `walUnlockExclusive()` wrap VFS shared-memory locking and become no-ops in exclusive heap-memory WAL mode.
- `walCleanupHash()`, `walIndexAppend()`, and `walIndexRecover()` maintain/rebuild wal-index hash tables. Recovery scans the WAL file under exclusive recovery locks, validates the WAL header and frames, records only committed frames in `hdr.mxFrame`/`hdr.nPage`, resets checkpoint/read marks, and logs recovery when frames are recovered.
- `sqlite3WalOpen()` allocates a `Wal` handle plus WAL fd storage, opens the `-wal` file, records read-only status, and selects heap-memory wal-index mode when requested.
- `walIteratorNext()`, `walMerge()`, and `walMergesort()` begin checkpoint iterator support by merging sorted frame-index lists while keeping the latest frame for duplicate database-page keys.

## Control Flow

Read transactions enter through `sqlite3PagerSharedLock()`. In rollback mode, the pager moves from `PAGER_OPEN` toward `PAGER_READER` by acquiring `SHARED_LOCK`, checking `hasHotJournal()`, and if necessary upgrading directly to `EXCLUSIVE_LOCK` to run `pagerSyncHotJournal()` and `pager_playback()`. Once any hot journal is settled, the cache is invalidated if the database version bytes changed, WAL is opened if a valid `-wal` file exists, and `dbSize` is populated. In WAL mode, the read path calls `pagerBeginReadTransaction()`, which ends any previous read transaction, starts a snapshot with `sqlite3WalBeginReadTransaction()`, and resets the pager cache if the WAL snapshot changed.

Page acquisition flows through `sqlite3PagerAcquire()`. It first asks `PCache` for the page. Existing initialized pages return immediately; new pages are either zeroed for `noContent`, memory DB, or beyond-end reads, or filled by `readDbPage()`. WAL reads consult `sqlite3WalRead()` before the database file. The FoundationDB read-only WAL branch tries a zero-copy database read for non-WAL frames and marks the page so later page-cache release logic can unpin it.

Write transactions start in `sqlite3PagerBegin()`. Rollback mode obtains a `RESERVED_LOCK`, optionally upgrades to exclusive, and snapshots `dbOrigSize`, `dbFileSize`, and `journalOff`. WAL mode obtains the WAL write lock and may also force database-file exclusive mode for exclusive locking. The first `sqlite3PagerWrite()` on a page opens the journal with `pager_open_journal()`, writes the original page image to the journal if needed, updates journal/savepoint bitvecs, and marks the page dirty. Spill pressure calls `pagerStress()`, which either appends a WAL frame or syncs the journal before writing a dirty page to the database file.

Rollback-mode commit is two-phase. `sqlite3PagerCommitPhaseOne()` updates page-1 change counters, journals truncation victims, writes any master-journal pointer, syncs the rollback journal, writes dirty pages, truncates or extends the database image, and syncs the database file. `sqlite3PagerCommitPhaseTwo()` then finalizes the journal by close/delete, truncate-to-zero, or zero-header depending on journal mode and exclusive mode; this is the point where rollback-mode commit becomes permanent. WAL-mode commit writes dirty pages as frames through `pagerWalFrames()`; final transaction cleanup goes through `pager_end_transaction()` and `sqlite3WalEndWriteTransaction()`.

Rollback has separate paths. Full rollback calls `sqlite3PagerRollback()`, which uses `pager_playback()` for rollback journals, `pagerPlaybackSavepoint()` and `sqlite3WalUndo()` for WAL, or finalizes an unopened/no-change journal directly. Savepoint rollback uses `pagerPlaybackSavepoint()` to replay the relevant main-journal segments and then sub-journal records, using `Bitvec` state so each page is restored once.

WAL recovery starts when a writer with the appropriate locks calls `walIndexRecover()`. It locks all shared-memory lock bytes other than already-held writer/checkpoint bytes, validates the WAL header, scans frames in file order, appends valid frames to wal-index hash tables, and only advances the durable snapshot when it sees commit frames. It then writes a fresh wal-index header and resets checkpoint metadata.

## State and Persistence Behavior

Persistent rollback-journal state includes journal headers, page records, checksums, master-journal pointers, and journal finalization mode. `PAGER_JOURNALMODE_DELETE` removes the journal, `TRUNCATE` truncates it, `PERSIST` zeroes the first header, `MEMORY` uses an in-memory journal descriptor, and `OFF` weakens rollback guarantees. `journalOff`, `journalHdr`, `nRec`, `setMaster`, `pInJournal`, and savepoint bitvecs track what has been recorded and what must be synced before database pages can be overwritten.

Persistent database state includes page content, database size, page-1 change counter at offset 24, version-valid-for counter at offset 92, SQLite version at offset 96, file truncation/extension state, and cached `dbFileVers` bytes used for cache invalidation. `dbSize`, `dbOrigSize`, `dbFileSize`, `dbHintSize`, and `mxPgno` are the pager's in-memory model of that state.

WAL persistent state is the `-wal` file: a 32-byte header plus 24-byte frame headers and page data. Frames become part of a committed snapshot only when the frame header's truncate/database-size field is nonzero. Salts and checksums prevent old frames and partially written frames from being accepted after crash or checkpoint reuse.

The wal-index is intentionally transient shared memory or heap memory in exclusive mode. It is rebuilt from the WAL by `walIndexRecover()`, stores native-endian metadata, duplicated headers with checksums, reader marks, checkpoint backfill count, frame-to-page arrays, and hash tables. It is not a persistent cross-platform format.

Pager error state is conservative. `pager_error()` moves the pager to `PAGER_ERROR` for `SQLITE_FULL` or `SQLITE_IOERR` class errors, causing major APIs to return the saved error until the cache is discarded and locks/journals are cleaned up. This prevents possibly corrupt cache contents from being reused after failed I/O.

## Dependencies and Integration Points

This chunk depends on earlier pager definitions in the same amalgamation: `Pager`, `PgHdr`, `PagerSavepoint`, pager state constants, lock constants, journal helpers such as `readJournalHdr()`, `writeJournalHdr()`, `zeroJournalHdr()`, `readMasterJournal()`, `pageInJournal()`, `subjRequiresPage()`, `pagerUseWal()`, `pagerLockDb()`, and `pagerUnlockDb()`.

It integrates heavily with the VFS layer through `sqlite3OsOpen`, `Read`, `Write`, `Sync`, `Truncate`, `FileSize`, `Access`, `Delete`, `FileControl`, `ShmMap`, `ShmLock`, `ShmBarrier`, and `ShmUnmap`. Correctness depends on VFS device-characteristic flags such as `SQLITE_IOCAP_SAFE_APPEND`, `SEQUENTIAL`, `ATOMIC`, and `UNDELETABLE_WHEN_OPEN`, plus FoundationDB's additional zero-copy methods.

It depends on PCache APIs for cache allocation, dirty-list handling, refcounts, page movement, clean/dirty flags, sync-flag clearing, truncation, and stress callbacks. It also integrates with backup APIs (`sqlite3BackupRestart()`, `sqlite3BackupUpdate()`), bitvec allocation for journal/savepoint membership, optional codec transforms, malloc fault injection/test macros, and btree-facing pager APIs.

WAL integration points include pager calls into `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalRead()`, `sqlite3WalFrames()`, `sqlite3WalBeginReadTransaction()`, `sqlite3WalEndReadTransaction()`, `sqlite3WalBeginWriteTransaction()`, `sqlite3WalEndWriteTransaction()`, `sqlite3WalUndo()`, `sqlite3WalSavepoint()`, `sqlite3WalSavepointUndo()`, `sqlite3WalCheckpoint()`, and related exclusive-mode helpers defined elsewhere in `wal.c`.

The public surface to upper SQLite layers is the `SQLITE_PRIVATE sqlite3Pager*` API set, used primarily by btree, pragma/opcode handling, backup, WAL checkpoint APIs, and codec-enabled builds.

## Risks

- Pager state transitions are crash-safety critical. Moving to `WRITER_DBMOD` before the journal is durable, clearing `PGHDR_NEED_SYNC` too early, or finalizing the journal before database sync can corrupt the database after power loss.
- Journal-header and `nRec` handling is subtle. Incorrect handling of persistent-journal tails, safe-append assumptions, full-sync ordering, or the ticket #2565 zero-record case can cause recovery to replay stale or incomplete records.
- Savepoint rollback depends on correct bitvec accounting across main journal, sub-journal, moved pages, and truncation. Missing a `subjournalPage()` call can make `ROLLBACK TO` restore the wrong image or fail after cache spill.
- Page movement and auto-vacuum are high risk because cache page numbers, dirty flags, `PGHDR_NEED_SYNC`, journal membership, and in-memory database rollback copies must remain coherent.
- WAL checksum, salt, and byte-order code defines the boundary between valid committed frames and garbage. Any drift in `walEncodeFrame()`, `walDecodeFrame()`, or recovery can accept torn writes or reject valid commits.
- WAL shared-memory locking is concurrency-sensitive. Reader marks, recovery locks, checkpoint locks, writer locks, and exclusive heap-memory mode must match VFS semantics or readers/checkpointers/writers can observe inconsistent snapshots.
- `walIndexAppend()` and `walCleanupHash()` must preserve hash-table reachability and last-frame lookup semantics. Off-by-one errors around `HASHTABLE_NPAGE_ONE` and later blocks can make reads find stale page versions.
- Read-only zero-copy integration assumes `xReadZeroCopy()` and `xReleaseZeroCopy()` obey pager lifetime, alignment, and immutability expectations. Incorrect VFS behavior could leave cache pages pointing at invalid memory or bypass codec expectations.
- `journal_mode=OFF`, `noSync`, and temp-file paths intentionally weaken durability. Callers and tests need to distinguish expected data-loss windows from corruption in default durable modes.
- Codec-enabled builds increase risk because bytes are transformed at journal write/read, database write/read, WAL frame write, and backup update boundaries.

## Test and Validation Signals

Useful validation should include pager crash-recovery, savepoint, WAL, and VFS-behavior tests:

- Rollback-journal commit/rollback tests across `DELETE`, `TRUNCATE`, `PERSIST`, `MEMORY`, and `OFF` journal modes, including exclusive and normal locking modes.
- Power-failure or fault-injection tests around journal header writes, `nRec` updates, journal sync, database page writes, database truncation, and journal finalization.
- Hot-journal recovery tests where a journal exists with and without a master-journal pointer, with stale persistent-journal tail data, with short reads, and with invalid checksums.
- Savepoint tests that combine page modifications before/after savepoints, cache spills, page moves, database truncation/auto-vacuum, WAL savepoints, and nested release/rollback operations.
- WAL tests for read snapshots, writer rollback, WAL frame checksums, salt changes after checkpoint/reset, wal-index rebuild after deleting shared memory, read-only WAL access, and checkpoints with active readers.
- Concurrency tests with multiple readers, writers, and checkpointers exercising `WAL_READ_LOCK`, `WAL_WRITE_LOCK`, `WAL_CKPT_LOCK`, and `WAL_RECOVER_LOCK`.
- VFS matrix tests for `SAFE_APPEND`, `SEQUENTIAL`, `ATOMIC`, `UNDELETABLE_WHEN_OPEN`, shared-memory support, read-only WAL open, and temp-file behavior.
- FoundationDB-specific zero-copy tests that verify read-only WAL misses can use `xReadZeroCopy()`, fall back cleanly on failure or short/funny-length reads, release pins exactly once, and do not run through incompatible codec paths.
- Codec builds should validate encrypted or transformed page content through database reads/writes, rollback journals, sub-journals, WAL frames, and backup update hooks.
- Existing SQLite debug/test signals in this chunk include `assert_pager_state()`, `testcase()` coverage points, `SQLITE_CHECK_PAGES` page hashes, `SQLITE_ENABLE_EXPENSIVE_ASSERT` WAL hash reachability checks, `PAGERTRACE`, `IOTRACE`, `WALTRACE`, and simulated I/O error controls.

### subset-b-008411: lines 37429-45048

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 37429-45048

## Scope And Purpose

This chunk spans the end of SQLite's WAL implementation, the Btree mutex support block, the online backup API, VDBE memory/value helpers, VDBE construction and teardown helpers, record serialization/comparison helpers, and the opening safety checks for the VDBE public API layer.

The WAL section is responsible for checkpointing frames back into the database, opening consistent reader snapshots, writing committed frames, rolling back uncommitted WAL writes, savepoint state, WAL close/delete behavior, and locking-mode transitions. The backup section implements `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, progress accessors, and pager callbacks that keep an incremental backup consistent while the source changes. The VDBE sections manage `Mem` values, statement bytecode construction, statement halt/reset/finalize semantics, cursor cleanup, multi-database commit orchestration, record encoding/decoding, and index key comparison.

This chunk is persistence-critical: it controls when WAL data becomes durable database-file content, when database snapshots are considered safe, how backup copies are committed, how VM execution commits or rolls back transactions, and how on-disk record bytes are interpreted.

## Important APIs, Types, And Functions

WAL entry points in this range include `sqlite3WalClose`, `sqlite3WalBeginReadTransaction`, `sqlite3WalEndReadTransaction`, `sqlite3WalRead`, `sqlite3WalDbsize`, `sqlite3WalBeginWriteTransaction`, `sqlite3WalEndWriteTransaction`, `sqlite3WalUndo`, `sqlite3WalSavepoint`, `sqlite3WalSavepointUndo`, `sqlite3WalFrames`, `sqlite3WalCheckpoint`, `sqlite3WalCallback`, `sqlite3WalExclusiveMode`, and `sqlite3WalHeapMemory`.

Important WAL helpers include `walIteratorInit`, `walIteratorFree`, `walBusyLock`, `walPagesize`, `walCheckpoint`, `walIndexTryHdr`, `walIndexReadHdr`, `walTryBeginRead`, and `walRestartLog`. They operate on `Wal`, `WalIterator`, `WalIndexHdr`, `WalCkptInfo`, hash-table segments, read marks, WAL locks, checksums, salt values, and VFS file handles.

The Btree mutex block defines `MemPage`, `BtLock`, `Btree`, and mutex-array routines used to lock shared btrees in stable pointer order. These functions are integrated later with VDBE bytecode execution through `sqlite3VdbeUsesBtree()` and `sqlite3VdbeMutexArrayEnter()`.

Backup APIs and helpers include `sqlite3_backup_init`, `sqlite3_backup_step`, `sqlite3_backup_finish`, `sqlite3_backup_remaining`, `sqlite3_backup_pagecount`, `sqlite3BackupUpdate`, `sqlite3BackupRestart`, `sqlite3BtreeCopyFile`, `findBtree`, `setDestPgsz`, `backupOnePage`, `backupTruncateFile`, and `attachBackupObject`. The central state object is `struct sqlite3_backup`, with source/destination handles, btrees, progress counters, current page, destination lock state, schema cookie, error code, and pager callback linkage.

VDBE `Mem` helpers include `sqlite3VdbeChangeEncoding`, `sqlite3VdbeMemGrow`, `sqlite3VdbeMemMakeWriteable`, `sqlite3VdbeMemExpandBlob`, `sqlite3VdbeMemNulTerminate`, `sqlite3VdbeMemStringify`, `sqlite3VdbeMemFinalize`, `sqlite3VdbeMemReleaseExternal`, `sqlite3VdbeMemRelease`, numeric conversion helpers, setters for NULL/int/double/zeroblob/rowset/string, copy/move helpers, `sqlite3MemCompare`, `sqlite3VdbeMemFromBtree`, and `sqlite3ValueText`/`sqlite3ValueNew`/`sqlite3ValueFromExpr`/`sqlite3ValueSetStr`/`sqlite3ValueFree`/`sqlite3ValueBytes`.

VDBE construction and lifecycle helpers include `sqlite3VdbeCreate`, `sqlite3VdbeSetSql`, `sqlite3_sql`, opcode add/change helpers, label resolution, `sqlite3VdbeTakeOpArray`, `sqlite3VdbeUsesBtree`, debug/explain printing, `sqlite3VdbeMakeReady`, `sqlite3VdbeFreeCursor`, `sqlite3VdbeFrameRestore`, `sqlite3VdbeSetNumCols`, `sqlite3VdbeSetColName`, `sqlite3VdbeCloseStatement`, `sqlite3VdbeCheckFk`, `sqlite3VdbeHalt`, `sqlite3VdbeReset`, `sqlite3VdbeFinalize`, `sqlite3VdbeDeleteObject`, `sqlite3VdbeDelete`, and `sqlite3VdbeCursorMoveto`.

Record helpers include `sqlite3VdbeSerialType`, `sqlite3VdbeSerialTypeLen`, `sqlite3VdbeSerialPut`, `sqlite3VdbeSerialGet`, `sqlite3VdbeRecordUnpack`, `sqlite3VdbeDeleteUnpackedRecord`, `sqlite3VdbeRecordCompare`, `sqlite3VdbeIdxRowid`, and `sqlite3VdbeIdxKeyCompare`. This amalgamation has a notable extended `sqlite3VdbeRecordCompare()` signature with `startField` and `pRestartField`, allowing comparison to resume after loading more partial key data.

The chunk ends at `sqlite3_expired`, `vdbeSafety`, and `vdbeSafetyNotNull`, which guard public statement APIs against finalized or NULL prepared statements.

## Control Flow

WAL checkpointing starts with `sqlite3WalCheckpoint()`: it obtains `WAL_CKPT_LOCK`, optionally obtains `WAL_WRITE_LOCK` for full/restart checkpoints, reads or reconstructs the wal-index header, validates the page-size buffer, calls `walCheckpoint()`, reports log/backfill counts, clears a stale local header if needed, and releases locks.

`walCheckpoint()` builds a sorted `WalIterator` over WAL frames, computes `mxSafeFrame` from active reader marks, takes `WAL_READ_LOCK(0)` while backfilling, optionally syncs the WAL, hints database file size, copies eligible frame payloads from WAL offsets to database page offsets, truncates and syncs the database if all frames are checkpointed, then advances `nBackfill`. Passive checkpoints tolerate busy readers by limiting safe backfill and converting reader-related `SQLITE_BUSY` to success. Restart checkpoints additionally wait for all read locks so the next writer can wrap the WAL.

Read transaction startup flows through `sqlite3WalBeginReadTransaction()` and repeated `walTryBeginRead()` calls. It reads the wal-index header without a lock, retries with `WAL_WRITE_LOCK` and recovery if the header is dirty/corrupt, may bypass the WAL with `WAL_READ_LOCK(0)` if all frames are backfilled, otherwise chooses a read-mark slot not greater than `mxFrame`, locks it shared, and verifies both the read mark and wal-index header after a memory barrier. Transient races return `WAL_RETRY`; excessive retries sleep with increasing delay and eventually return `SQLITE_PROTOCOL`.

WAL page reads use the snapshot header's `mxFrame`, skip WAL access when the snapshot is empty or read-lock 0 is held, search wal-index hash tables from newest segment to oldest, bound matches to frames visible to the reader, detect excessive hash collisions as corruption, and read the selected frame payload from the WAL file.

WAL writes start with `sqlite3WalBeginWriteTransaction()` requiring an existing read transaction and a matching wal-index header snapshot to avoid forked histories. `sqlite3WalFrames()` may reset the log with `walRestartLog()`, writes a new WAL header for the first frame, writes frame headers and page data, may pad to a sector boundary before syncing, appends frame/page mappings to the wal-index, updates `mxFrame`, `nPage`, checksums, and `iCallback`, and writes the wal-index header on commit. Undo and savepoint rollback restore `mxFrame`/checksums and clean hash entries.

Backup control begins with `sqlite3_backup_init()` resolving source and destination btrees, setting destination page size to source page size, and incrementing the source backup count. `sqlite3_backup_step()` locks source/destination state, starts a destination write transaction and source read transaction as needed, copies up to `nPage` pages through `backupOnePage()`, attaches to the source pager if incremental work remains, and on completion updates the destination schema version, handles page-size/pending-byte truncation details, commits the destination transaction, and records progress. `sqlite3_backup_finish()` detaches the object, rolls back any unfinished destination work, stores the final error on the destination handle, and frees user-created backup handles.

`sqlite3BackupUpdate()` is the live consistency hook: if a source page already copied by an active backup changes, it re-copies the new page image into the destination. `sqlite3BackupRestart()` resets `iNext` to page 1 when external source changes make previously copied pages untrustworthy. `sqlite3BtreeCopyFile()` wraps the backup machinery for VACUUM-style complete btree copies using a stack `sqlite3_backup` object.

VDBE compilation builds bytecode with add-op helpers, negative labels, P4 ownership types, and optional debug comments. `resolveP2Values()` resolves labels, marks op flags, determines read-only status, and records maximum function argument count. `sqlite3VdbeMakeReady()` transitions the VM from init to run state and allocates registers, bound variables, cursor slots, function argument arrays, and variable-name arrays, first reusing unused opcode-array tail space and then falling back to a single heap allocation.

VDBE halt/reset flow is the transaction boundary for statement execution. `sqlite3VdbeHalt()` closes cursors, locks required btrees, classifies special errors, performs statement rollback or full transaction rollback when pager/cache state may be inconsistent, checks immediate and deferred foreign keys, commits autocommit transactions through `vdbeCommit()`, releases or rolls back statement savepoints, updates change counts, resets schema state on failed internal changes, releases btree mutexes, marks the VM halted, and invokes unlock-notify callbacks. `sqlite3VdbeReset()` transfers VM error state to the database handle, cleans result memory, profiles if enabled, and returns to init state. Finalize calls reset if needed and unlinks/frees the VM.

Record comparison flow unpacks serialized records into `Mem` cells, compares storage classes with SQLite ordering (`NULL`, numeric, text with collation, blob), handles DESC sort inversion, rowid-ignoring index comparisons, prefix/incremental-key flags, and corruption checks. The extended partial-record path in `sqlite3VdbeRecordCompare()` returns equality plus `pRestartField` when the left key buffer is incomplete and more bytes are required to decide the comparison.

## State And Persistence Behavior

WAL persistence is guarded by explicit fsync order. During checkpoint, the WAL is synced before frames are copied to the database file, and the database file is synced only when all WAL content has been copied and the database can safely replace the WAL as durable state. `nBackfill` is the persistent shared-memory progress marker for checkpointed frames; it only increases in `walCheckpoint()` except resets/recovery.

WAL read state is snapshot-based. `pWal->hdr` caches a verified wal-index header, `pWal->readLock` selects either database-only reads or a WAL read-mark slot, and memory barriers plus duplicated wal-index headers defend against torn concurrent reads. `pWal->writeLock`, `pWal->ckptLock`, `exclusiveMode`, `nCkpt`, salts, frame checksums, and `iCallback` model writer/checkpointer ownership and callback state.

`walRestartLog()` is a key persistence transition. When every frame has been backfilled and all nonzero reader locks can be obtained, it increments checkpoint salt state, resets `mxFrame` to zero, writes a new wal-index header, clears `nBackfill`, marks reader slots unused, and reacquires a WAL-using read snapshot for the writer.

Backup state is persistent at the destination pager/btree level. Page copies are journaled via normal pager writes, completion updates the schema cookie, truncation is coordinated with pager image truncation and commit phase one, and a destination transaction is committed only after all source pages are copied. Until finish or successful completion, `sqlite3_backup.rc`, `iNext`, `nRemaining`, `nPagecount`, `bDestLocked`, and `isAttached` describe resumable copy state.

VDBE `Mem` state is intensely ownership-sensitive. Flags distinguish NULL, integer, real, text, blob, rowset, aggregate, frame, static, ephemeral, dynamic, zero-filled blob tail, and nul-terminated storage. Helpers centralize destructor calls, `zMalloc` reuse, encoding conversion, shallow vs full copies, and length-limit checks. Incorrect flags can leak memory, double-free, compare invalid bytes, or return a pointer with the wrong lifetime.

VDBE transaction state lives in `db->autoCommit`, active/write VDBE counts, `db->nStatement`, `p->iStatement`, deferred FK counters, change counters, savepoints, btree transaction state, and virtual table sync/commit hooks. `vdbeCommit()` uses a master journal for atomic multi-file rollback-mode commits, while simple single-file or in-memory/temp cases commit each btree directly.

Record serialization persists SQLite storage classes to disk. The serial type table maps NULL, integer widths, IEEE float, integer constants 0/1, blob, and text to compact byte formats. Integer and float byte order are normalized; mixed-endian 64-bit float configurations have explicit swap logic and debug assertions.

## Dependencies And Integration Points

The WAL code integrates with the VFS and pager through `sqlite3OsRead`, `sqlite3OsWrite`, `sqlite3OsSync`, `sqlite3OsTruncate`, `sqlite3OsFileSize`, `sqlite3OsFileControl`, `sqlite3OsSleep`, WAL shared-memory mapping/locking primitives, and pager-provided buffers. It depends on hash-table helpers and constants defined earlier in `wal.c`, including `WAL_READ_LOCK`, `WAL_WRITE_LOCK`, `WAL_CKPT_LOCK`, `WAL_RECOVER_LOCK`, `WAL_NREADER`, `HASHTABLE_NPAGE`, and `READMARK_NOT_USED`.

The backup API integrates database handles, btrees, pagers, source-pager backup callback lists, schema metadata, journal modes, pending-byte handling, page-size constraints, and the public `sqlite3_backup_*` API. It must cooperate with WAL mode, in-memory databases, codecs, and VACUUM's full-file copy path.

Btree mutex routines bridge connection-level mutexes, shared cache `BtShared` mutexes, and VDBE execution. They sort locks by `BtShared*` to avoid deadlock and maintain `wantToLock`/`locked` nesting state.

VDBE construction integrates parser/code generator output with execution. Opcode P4 ownership types reference collations, functions, key info, virtual tables, subprograms, memory values, integer arrays, and allocated strings. `sqlite3VdbeUsesBtree()` records which attached btrees a statement may touch so execution can acquire mutexes in the same global order.

VDBE halt integrates with pager/btree transaction phases, virtual table `xSync`/commit/rollback hooks, commit hooks, rollback hooks, foreign key enforcement, savepoints, schema invalidation, unlock-notify, and statement error propagation to `sqlite3_errcode()`/`sqlite3_errmsg()`.

Record helpers integrate the btree cursor layer, collation sequences, `KeyInfo`, `UnpackedRecord`, OP_MakeRecord output, OP_IsUnique prefix search, index rowid extraction, and cursor movement. They are central to table/index lookup correctness.

## Risks And Edge Cases

WAL checkpointing is concurrency- and crash-safety sensitive. A wrong `mxSafeFrame`, missed read-mark check, or premature database sync/truncate can overwrite pages needed by active readers or leave the database file ahead of durable WAL state after power loss.

The wal-index header is read lock-free first, so the duplicate-header checksum protocol and memory barriers are non-negotiable. Weakening `walIndexTryHdr()` or skipping the retry/recovery path can accept torn shared-memory state.

Read transaction startup intentionally has many `WAL_RETRY` paths. Changes around read-lock 0, read-mark selection, or post-lock header comparison can create snapshot corruption that appears only under concurrent writer/checkpointer races.

`sqlite3WalFrames()` writes frame bytes before appending wal-index entries and before publishing the commit header. Reordering those updates risks readers seeing incomplete frames or checkpointers missing committed frames. Sector-padding copies of the last frame are also subtle because they affect durable commit behavior under `sync_flags`.

Backup with differing source/destination page sizes is especially risky near the pending-byte page. The code skips pending-byte pages, may manually write source pages that straddle the destination pending-byte area, truncates the destination file outside normal page writes, and relies on pager phase-one journaling before direct file writes.

`sqlite3_backup_finish()` always rolls back an unfinished destination btree. Callers must not assume partially copied data is usable unless `sqlite3_backup_step()` reached `SQLITE_DONE` and finish returns `SQLITE_OK`.

`Mem` ownership flags are a persistent source of hazards. Shallow copies must not outlive their source bytes, dynamic destructors must be called exactly once, zero blobs must be expanded before mutation, and conversion helpers assume the database mutex is held when a `db` pointer exists.

`sqlite3VdbeHalt()` encodes SQLite's statement and transaction semantics. Small changes can regress conflict actions, autocommit behavior, deferred FK enforcement, active VDBE counters, statement journal rollback, virtual table commit ordering, or multi-database atomic commit.

The record comparison extension for partial keys is a local divergence from stock SQLite behavior. `startField`/`pRestartField` must remain synchronized with btree/pager callers that provide partial record buffers; returning a definitive comparison too early can misorder keys, while returning restart fields incorrectly can cause repeated work or missed comparisons.

Serialization/deserialization uses aliasing and byte-order-sensitive casts for integer and floating-point values. Compiler, architecture, or sanitizer changes should be tested around signed 6-byte/8-byte integers, NaN handling, and mixed-endian float builds.

## Test Signals

WAL test signals should include concurrent readers, writers, and checkpointers under PASSIVE, FULL, and RESTART modes; wal-index dirty-header recovery; WAL wrap/restart; active reader limiting of `nBackfill`; large-page and 65536-byte page sizes; injected `SQLITE_BUSY`, I/O errors, sync failures, and crash-recovery cases around checkpoint/write ordering.

Backup test signals should cover incremental and all-at-once backups, source changes after pages are copied, external source changes forcing restart, WAL-mode destination page-size mismatch returning `SQLITE_READONLY`, in-memory destination page-size mismatch, pending-byte-page handling with differing page sizes, finish after errors, and VACUUM `sqlite3BtreeCopyFile()` behavior.

VDBE memory tests should exercise text/blob ownership modes (`STATIC`, `TRANSIENT`, `DYNAMIC`, ephemeral), UTF-8/UTF-16 conversion, BOM handling, zero-blob expansion, rowset release, aggregate finalization, shallow/full copy lifetimes, length-limit `SQLITE_TOOBIG`, OOM behavior, and collation comparisons across encodings.

VDBE lifecycle tests should cover successful autocommit commit, statement rollback on `OE_Abort`, `OE_Fail` conflict handling, special errors (`NOMEM`, `IOERR`, `FULL`, `INTERRUPT`), deferred and immediate FK violations, commit hook failure, virtual table sync/commit ordering, multi-database master-journal commit, reset/finalize after partial execution, expired/run-only-once statements, and cursor invalidation after rollback.

Record helper tests should cover every serial type, integer boundary widths, file-format 4 integer constants, NaN deserialization, mixed text/blob comparisons, DESC sort order, prefix and incremental key flags, rowid extraction corruption checks, `UNPACKED_IGNORE_ROWID`, and the partial-record `pRestartField` path added to `sqlite3VdbeRecordCompare()`.

Static review signals in the code include many `assert()`, `testcase()`, `NEVER()`, and corruption returns (`SQLITE_CORRUPT_BKPT`) around boundary conditions. These mark intended fuzz/injection targets for this chunk.

### subset-b-008412: lines 45049-52795

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 45049-52795

## Scope

This chunk spans the tail of SQLite's public VDBE API layer, SQL trace expansion, and the beginning-to-middle of the VDBE interpreter. It starts with statement finalization/reset and value/result helpers, then covers host-parameter binding, column extraction, statement metadata, `sqlite3_step()` execution, and the opcode implementations from `OP_Goto` through the start of `OP_VNext`. The requested range ends inside `OP_VNext`; virtual-table iteration completion and later VDBE halt/error epilogue code are outside this chunk.

## Purpose

The code connects public `sqlite3_stmt`, `sqlite3_value`, and `sqlite3_context` APIs to the internal `Vdbe` and `Mem` representations, then interprets compiled SQL bytecode. Its main responsibilities are:

- Manage a prepared statement's lifecycle: finalize, reset, clear bindings, step, reprepare on schema changes, expose statement metadata/status, and iterate statements on a connection.
- Convert values between SQLite storage classes and C API views, including UTF-8/UTF-16 text, blobs, integers, doubles, nulls, zeroblobs, and numeric affinity.
- Provide user-defined scalar/aggregate function result APIs, aggregate contexts, auxiliary data caches, collation context, and function error reporting.
- Bind host parameters and track whether changed bindings require automatic reprepare because query-plan-sensitive parameters changed.
- Execute VDBE opcodes for expression evaluation, row production, record encode/decode, B-tree cursor navigation, table/index mutations, transaction/savepoint control, schema maintenance, rowsets, triggers, foreign keys, aggregates, WAL/journal pragmas, vacuum, shared-cache locks, and virtual table callbacks.

## Important APIs, Types, and Functions

- Public statement APIs:
  - `sqlite3_finalize()` calls `sqlite3VdbeFinalize()` under the connection mutex and treats NULL as `SQLITE_OK`.
  - `sqlite3_reset()` calls `sqlite3VdbeReset()`, then `sqlite3VdbeMakeReady()` to return the VM to its initial executable state.
  - `sqlite3_clear_bindings()` releases every `Vdbe.aVar[]` `Mem`, sets it to NULL, and expires v2 statements if any parameter is plan-sensitive.
  - `sqlite3_step()` is the top-level C API wrapper around `sqlite3Step()`, with a bounded schema-reprepare loop.

- Value and result APIs:
  - `sqlite3_value_blob/text/text16/bytes/double/int/int64/type()` read from internal `Mem` cells and may expand zeroblobs or convert encodings.
  - `sqlite3_result_blob/text/text16/double/int/int64/null/value/zeroblob/error*()` write the function result into `sqlite3_context.s`, using `setResultStrOrError()` to translate oversized string/blob results into `SQLITE_TOOBIG`.
  - `sqlite3_result_error_nomem()` marks both the context error and `db->mallocFailed`, which is later observed by VDBE execution.

- User function context APIs:
  - `sqlite3_user_data()` and `sqlite3_context_db_handle()` expose `FuncDef.pUserData` and the owning `sqlite3 *`.
  - `sqlite3_aggregate_context()` allocates persistent per-group memory in `pCtx->pMem` and marks it `MEM_Agg`.
  - `sqlite3_get_auxdata()`/`sqlite3_set_auxdata()` manage per-argument auxiliary values in `VdbeFunc.apAux[]`, including destructor invocation on replacement or failed allocation.
  - `sqlite3InvalidFunction()` is a placeholder function body used for names that resolve but must be implemented by virtual-table overload resolution.

- Column and binding APIs:
  - `columnMem()` validates `pResultSet` and column bounds, returning a static NULL `Mem` and setting `SQLITE_RANGE` for invalid access.
  - `sqlite3_column_*()` wrappers call the corresponding `sqlite3_value_*()` conversion and then `columnMallocFailure()` so conversion allocation failures affect subsequent step/reset/finalize behavior.
  - `columnName()` reads display names, decltypes, and optional origin metadata from `Vdbe.aColName[]` with the right name slot (`COLNAME_NAME`, `COLNAME_DECLTYPE`, `COLNAME_DATABASE`, `COLNAME_TABLE`, `COLNAME_COLUMN`).
  - `vdbeUnbind()` enforces that binding happens only on idle statements, validates 1-based parameter indices, clears the old `Mem`, updates `db` error state, and marks statements expired when `expmask` says a new value may change the plan.
  - `bindText()` centralizes blob/text binding, destructor handling, encoding conversion, and error propagation.
  - `createVarMap()`, `sqlite3_bind_parameter_name()`, and `sqlite3VdbeParameterIndex()` derive named-parameter mappings from `OP_Variable` opcodes.
  - `sqlite3TransferBindings()` moves `Mem` bindings between two statements on the same connection; the deprecated public wrapper checks parameter-count equality and expires both statements if needed.

- VDBE support routines:
  - `doWalCallbacks()` runs registered WAL callbacks after successful statement completion.
  - `sqlite3VdbeExpandSql()` renders trace SQL with host parameters substituted as SQL literals when not nested, or comments out raw SQL when VDBE execution is nested.
  - `sqlite3VdbeMemStoreType()`, `applyNumericAffinity()`, `applyAffinity()`, `sqlite3_value_numeric_type()`, and `sqlite3ValueApplyAffinity()` maintain the public storage-class view of `Mem` cells.
  - `allocateCursor()` stores `VdbeCursor` allocations in high-numbered `Mem` registers, optionally embedding a `BtCursor` and column type/offset arrays.
  - `importVtabErrMsg()` transfers `sqlite3_vtab.zErrMsg` into `Vdbe.zErrMsg`.

## Control Flow

`sqlite3_step()` enters `db->mutex`, calls `sqlite3Step()`, and if it sees `SQLITE_SCHEMA`, tries `sqlite3Reprepare()` up to five times before returning the final API-masked code. `sqlite3Step()` performs automatic reset for already-completed statements unless `SQLITE_OMIT_AUTORESET` restores legacy misuse behavior. On first execution it resets interruption state when no other VDBE is active, increments active/write VM counters, optionally starts profiling, and dispatches to `sqlite3VdbeExec()` or `sqlite3VdbeList()` for explain output. `SQLITE_DONE` runs WAL callbacks, and v2-prepared statements return the richer stored `p->rc` on errors.

`sqlite3VdbeExec()` is a tight interpreter loop over `p->aOp[pc]`. Before the switch it enters all required B-tree mutexes, resets result-set state, initializes progress callback accounting, and optionally emits debug listings. Each iteration checks allocation failure, optional test interrupts, progress callbacks, and operand pre-release flags. Many opcodes update `pc` directly for jumps; row-producing `OP_ResultRow` sets `p->pResultSet`, stores public types on output registers, closes any statement transaction used by `SQLITE_CountRows`, sets `p->pc = pc + 1`, returns `SQLITE_ROW`, and exits through the shared return path outside this chunk.

The opcode groups in this range are:

- Control and constants: `OP_Goto`, `OP_Gosub`, `OP_Return`, `OP_Yield`, `OP_HaltIfNull`, `OP_Halt`, `OP_Integer`, `OP_Int64`, `OP_Real`, `OP_String8`, `OP_String`, `OP_Null`, `OP_Blob`, `OP_Variable`, `OP_Move`, `OP_Copy`, `OP_SCopy`, `OP_ResultRow`.
- Expression evaluation: concatenation, arithmetic, bit operations, casts, numeric/text affinity, boolean logic, null tests, comparison (`OP_Lt` through `OP_Ge`), vector comparison (`OP_Permutation`, `OP_Compare`, `OP_Jump`), scalar function invocation, and collation selection.
- Record and row access: `OP_Column`, `OP_Affinity`, `OP_MakeRecord`, `OP_RowData`/`OP_RowKey`, `OP_Rowid`, `OP_NullRow`.
- B-tree cursor and index operations: `OP_OpenRead`, `OP_OpenWrite`, `OP_OpenEphemeral`, `OP_OpenAutoindex`, `OP_OpenPseudo`, `OP_Close`, `OP_Seek*`, `OP_Seek`, `OP_Found`, `OP_NotFound`, `OP_IsUnique`, `OP_NotExists`, `OP_Sequence`, `OP_NewRowid`, `OP_Insert`, `OP_InsertInt`, `OP_Delete`, `OP_ResetCount`, `OP_Last`, `OP_Sort`, `OP_Rewind`, `OP_Next`, `OP_Prev`, `OP_IdxInsert`, `OP_IdxDelete`, `OP_IdxRowid`, `OP_IdxGE`, `OP_IdxLT`.
- Transaction and schema operations: `OP_Count`, `OP_Savepoint`, `OP_AutoCommit`, `OP_Transaction`, `OP_ReadCookie`, `OP_SetCookie`, `OP_VerifyCookie`, `OP_Destroy`, `OP_Clear`, `OP_CreateTable`, `OP_CreateIndex`, `OP_ParseSchema`, `OP_LoadAnalysis`, `OP_DropTable`, `OP_DropIndex`, `OP_DropTrigger`, `OP_IntegrityCk`.
- Higher-level runtime features: `OP_RowSetAdd`, `OP_RowSetRead`, `OP_RowSetTest`, `OP_Program`, `OP_Param`, `OP_FkCounter`, `OP_FkIfZero`, `OP_MemMax`, integer branch opcodes, `OP_AggStep`, `OP_AggFinal`, `OP_Checkpoint`, `OP_JournalMode`, `OP_Vacuum`, `OP_IncrVacuum`, `OP_Expire`, `OP_TableLock`, and virtual-table opcodes from `OP_VBegin` through the beginning of `OP_VNext`.

## State and Persistence Behavior

The persistent runtime state is mostly on `sqlite3`, `Vdbe`, `VdbeCursor`, `Mem`, and the B-tree/pager layers:

- Statement lifecycle fields such as `Vdbe.magic`, `pc`, `rc`, `expired`, `isPrepareV2`, `readOnly`, `pResultSet`, `zErrMsg`, `aCounter[]`, `nChange`, and binding array `aVar[]` determine public API behavior across calls.
- Connection-level counters and flags such as `activeVdbeCnt`, `writeVdbeCnt`, `autoCommit`, `isTransactionSavepoint`, `nSavepoint`, `nStatement`, `nDeferredCons`, `lastRowid`, `mallocFailed`, `errCode`, `u1.isInterrupted`, and callbacks are mutated by stepping, transaction opcodes, row modification opcodes, and error paths.
- `Mem` flags (`MEM_Null`, `MEM_Int`, `MEM_Real`, `MEM_Str`, `MEM_Blob`, `MEM_Zero`, `MEM_Dyn`, `MEM_Static`, `MEM_Ephem`, `MEM_RowSet`, `MEM_Agg`, `MEM_Frame`) encode ownership, storage class, and runtime object type. Many opcodes deliberately shallow-copy or deep-copy these cells and must keep ownership flags correct.
- Record persistence uses SQLite's serial record format: `OP_MakeRecord` writes a varint header of serial types followed by field bytes, while `OP_Column` parses and caches type/offset arrays in `VdbeCursor`.
- Table and index persistence is through `sqlite3Btree*` APIs. `OP_Insert`, `OP_Delete`, `OP_IdxInsert`, `OP_IdxDelete`, `OP_Clear`, `OP_Destroy`, and `OP_Create*` mutate database B-trees; `OP_Transaction`, `OP_Savepoint`, `OP_AutoCommit`, `OP_JournalMode`, `OP_Checkpoint`, `OP_Vacuum`, and `OP_IncrVacuum` affect transaction, journal, WAL, and vacuum state.
- Schema persistence and in-memory schema state are coordinated by cookie reads/writes and schema mutation opcodes. `OP_VerifyCookie` expires statements and resets in-memory schema on cookie mismatch; `OP_ParseSchema`, `OP_LoadAnalysis`, `OP_Drop*`, and `OP_Expire` update or invalidate schema-derived state.
- Trigger execution persists a call stack in `VdbeFrame` objects stored inside `MEM_Frame` registers. `OP_Program` swaps the active register/cursor/opcode arrays to the subprogram and restores later in `OP_Halt` outside this range's main entry point.
- Virtual table state is externalized through module cursors and callbacks. The interpreter sets `p->inVtabMethod` around selected calls to avoid unsafe schema invalidation and imports module error messages back into the VDBE.

## Dependencies and Integration Points

- Mutexing and thread-safety depend on `sqlite3_mutex_enter/leave`, `sqlite3VdbeMutexArrayEnter()`, and B-tree shared mutex helpers. Several opcodes assume the prepare path has declared B-tree usage in `p->btreeMask`.
- Memory management depends on `sqlite3DbMalloc*`, `sqlite3DbRealloc`, `sqlite3DbFree`, `sqlite3VdbeMemGrow`, `sqlite3VdbeMemRelease*`, `sqlite3VdbeMemMove`, and API-exit handling through `sqlite3ApiExit()`.
- Parser/code-generator contracts are encoded directly in opcode comments and assertions: operand flags, register ranges, `P4` union type (`P4_KEYINFO`, `P4_INT32`, `P4_FUNCDEF`, `P4_VDBEFUNC`, `P4_COLLSEQ`, `P4_MEM`, `P4_SUBPROGRAM`), and opcode ordering assumptions such as `OP_SeekLt` through `OP_SeekGt`.
- B-tree and pager integration includes cursor movement/fetching, transaction begin/statement begin/savepoint, root-page creation/drop/clear, autovacuum root moves, WAL checkpoint/close/set-version paths, journal mode switching, and table locks under shared cache.
- User-defined function integration flows through `FuncDef`, `sqlite3_context`, `sqlite3_value`, `VdbeFunc`, collation (`OP_CollSeq`), scalar `xFunc`, aggregate `xStep`/finalizer, and destructor semantics for result and auxdata ownership.
- Callback integration includes WAL hooks, profile callbacks, progress callbacks, update hooks, trace SQL expansion, and virtual-table module methods (`xBegin`, `xCreate`, `xDestroy`, `xOpen`, `xFilter`, `xColumn`, partial `xNext` setup).
- Compile-time feature gates materially change behavior: UTF-16, floating point, casts, trace, explain, deprecated APIs, WAL, pragma, vacuum/attach, autovacuum, analyze, integrity check, trigger, foreign key, autoincrement, shared-cache, virtual tables, test instrumentation, and debug/profile support.

## Risks and Edge Cases

- Binding while a statement is busy is explicit misuse. `vdbeUnbind()` logs this and returns `SQLITE_MISUSE_BKPT`; callers that pass custom destructors still need the destructor path to run on failed text/blob binding.
- Column accessor conversions can allocate after a row has been produced. `columnMallocFailure()` must convert `db->mallocFailed` into statement `SQLITE_NOMEM`; otherwise later `sqlite3_step()`/`finalize()` would hide conversion failure.
- `OP_Column` is a high-risk corruption boundary. It limits oversized headers, minimizes allocation for corrupt records, handles short records by returning NULL or a default `P4_MEM`, and validates header/data offsets before deserializing.
- `Mem` ownership flags are subtle. `OP_SCopy`, `OP_Copy`, `OP_ResultRow`, `OP_Function`, `OP_VColumn`, `OP_MakeRecord`, and `OP_Column` must avoid dangling ephemeral pointers, double frees, or losing dynamic allocations.
- Transaction opcodes reject commits, rollbacks, savepoint operations, and WAL mode transitions when other statements are active in incompatible ways. Mistakes here can produce overlapping statement transactions, locks held across callbacks, or inconsistent `autoCommit` state.
- `OP_NewRowid` has multiple edge cases: cached rowid use, `MAX_ROWID`, random rowid fallback, AUTOINCREMENT ceiling enforcement, root-frame register updates, and `SQLITE_FULL` after repeated random collisions.
- Schema-cookie handling deliberately treats normal SQL and virtual-table method execution differently to avoid invalidating a virtual table structure while its module is running prepared statements internally.
- Virtual table callbacks are external code. The interpreter imports module error strings, sets `inVtabMethod`, and must clean up cursors on allocation failure; module misuse or reentrancy can still surface as `SQLITE_LOCKED`, callback errors, or malloc state.
- `sqlite3VdbeExpandSql()` renders values for tracing and must avoid mis-tokenizing parameters inside comments, strings, and quoted identifiers. It also emits blob hex and escaped text, so length limits and encoding conversion failures matter.
- This chunk ends before the shared VDBE error labels (`no_mem`, `too_big`, `abort_due_to_error`, `vdbe_return`) and before completing `OP_VNext`; those paths are essential for full lifecycle analysis but are not in the requested range.

## Test Signals

- Public API behavior: finalizing/resetting NULL statements, resetting after `SQLITE_ROW`/`SQLITE_DONE`, clearing bindings, binding out-of-range indexes, binding while busy, parameter name/index lookup, binding transfer, statement readonly/status counters, and `sqlite3_next_stmt()` iteration.
- Value conversion: UTF-8/UTF-16 text accessors, blob/zeroblob expansion, numeric affinity, casts, arithmetic overflow fallback to floating point, divide/remainder by zero returning NULL, NaN to NULL, and string/blob length limit failures.
- Function APIs: scalar result setters, oversized result to `SQLITE_TOOBIG`, `sqlite3_result_error_nomem()`, aggregate context allocation and reuse, aggregate finalization, auxdata destructor order, collation-sensitive functions, and invalid overloaded functions.
- Step execution: autorereset compatibility, schema-change reprepare limit, profile/progress callback firing, interrupt handling, WAL callback invocation after `SQLITE_DONE`, and API error masking.
- Record/cursor behavior: `OP_MakeRecord`/`OP_Column` round trips, corrupt record detection, short record defaults, rowdata/rowkey reads, pseudo-table column extraction, deferred seek, and cursor cache invalidation after movements or writes.
- Persistence operations: read/write transaction start, statement journal creation, savepoint begin/release/rollback, autocommit commit/rollback busy cases, insert/update/delete hooks, row count changes, root page create/drop/clear, schema cookie verify/set, pragma journal mode transitions, WAL checkpoint result registers, vacuum/incremental vacuum, and shared-cache table locks.
- Query execution opcodes: comparison with collations and NULL flags, vector compare/permutation, rowset duplicate suppression, trigger recursion limit and `old/new` parameter copying, foreign-key counters, AUTOINCREMENT max tracking, and aggregate step/final error propagation.
- Virtual table behavior in this range: `xBegin`, `xCreate`, `xDestroy`, `xOpen`, `xFilter`, `xColumn`, error-message import, empty-filter jump, null-row handling, and setup for `xNext` in `OP_VNext` with the remaining body covered by the next chunk.

### subset-b-008413: lines 52796-60569

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 52796-60569

## Scope

This chunk covers a large middle section of the SQLite amalgamation embedded under the FoundationDB SQLite contribution. It begins in the final cases of the VDBE opcode interpreter, then spans complete or partial amalgamated modules:

- Tail of `vdbe.c`: virtual table update/rename opcodes, pager pragmas, tracing, interpreter profiling/debug epilogue, and error exits.
- `vdbeblob.c`: incremental BLOB handle implementation.
- `journal.c`: lazy on-disk journal wrapper used with `SQLITE_ENABLE_ATOMIC_WRITE`.
- `memjournal.c`: in-memory rollback journal implementation.
- `walker.c`: generic expression/SELECT tree traversal.
- `resolve.c`: identifier, alias, function, aggregate, and SELECT name resolution.
- Large part of `expr.c`: expression affinity/collation, expression allocation/duplication/deletion, `IN`/subquery code generation, boolean jump codegen, aggregate analysis, and temporary register management.
- `alter.c`: `ALTER TABLE RENAME` and `ALTER TABLE ADD COLUMN` implementation support.
- Start of `analyze.c`: `ANALYZE` code generation and the beginning of `sqlite3AnalysisLoad()`.

The chunk starts after earlier VDBE opcode cases and ends inside `sqlite3AnalysisLoad()`, after existing analysis statistics have been cleared and before the rest of sqlite_stat table loading is shown.

## Purpose

This range implements several core SQLite execution and compilation services:

- It finishes VDBE runtime behavior for virtual tables, page-count pragmas, tracing, and error unwinding.
- It exposes the public incremental BLOB APIs by borrowing a VDBE b-tree cursor while a prepared statement keeps the target row open.
- It provides journal file implementations used by pager rollback behavior, including pure memory journals and delayed materialization of journal files for atomic-write optimizations.
- It provides tree-walker infrastructure used by resolver, optimizer, code generator, and aggregate analyzer passes.
- It resolves SQL identifiers into table columns, trigger pseudo-table references, result aliases, functions, aggregate functions, and compound `ORDER BY` targets.
- It builds, copies, compares, deletes, and emits VDBE bytecode for expression trees.
- It implements schema-text rewrites and schema reloads for legacy SQLite `ALTER TABLE` operations.
- It generates and loads planner statistics for `ANALYZE` using `sqlite_stat1` and optionally `sqlite_stat2`.

## Important APIs, Types, and Functions

### VDBE Tail

Important opcodes in the opening section are:

- `OP_VRename` calls a virtual table module's `xRename()` implementation and imports any virtual-table error message.
- `OP_VUpdate` marshals memory cells into `sqlite3_value*` arguments for `xUpdate()`, updates `db->lastRowid` when requested, and increments the statement change counter.
- `OP_Pagecount` and `OP_MaxPgcnt` expose b-tree page count and maximum page-count behavior for pager pragmas.
- `OP_Trace` expands SQL text and invokes `db->xTrace`, with debug-only SQL trace logging.

The interpreter epilogue records VDBE profile counters, optionally prints register traces, funnels fatal exits through `vdbe_error_halt`, normal returns through `vdbe_return`, and maps `too_big`, `no_mem`, generic error, and interrupt labels into SQLite error codes.

### Incremental BLOB I/O

`Incrblob` is the handle behind `sqlite3_blob*`. It stores access flags, blob size, byte offset inside the record payload, column index, borrowed `BtCursor`, owning statement, and database handle.

Key functions:

- `blobSeekToRow()` binds/seeks the hidden VDBE statement to a rowid, verifies the target column has TEXT or BLOB serial type, records payload offset/size, caches overflow pages, and invalidates the handle on error by finalizing the statement.
- `sqlite3_blob_open()` validates the target table and column, rejects virtual tables/views, rejects writable handles on indexed or foreign-key child columns, builds a small VDBE program (`OP_Transaction`, `OP_VerifyCookie`, `OP_TableLock`, `OP_OpenRead`/`OP_OpenWrite`, `OP_NotExists`, `OP_Column`, `OP_ResultRow`), and seeks to the requested row.
- `blobReadWrite()` enforces bounds, checks invalidated handles, calls `sqlite3BtreeData()` or `sqlite3BtreePutData()` under cursor mutex discipline, and propagates b-tree errors through the VDBE and db error state.
- Public APIs `sqlite3_blob_close()`, `sqlite3_blob_read()`, `sqlite3_blob_write()`, `sqlite3_blob_bytes()`, and `sqlite3_blob_reopen()` wrap that state.

### Journal Implementations

With `SQLITE_ENABLE_ATOMIC_WRITE`, `JournalFile` subclasses `sqlite3_file` and starts with an in-memory buffer. `createFile()` lazily opens the real VFS file and flushes buffered bytes. `jrnlRead()`, `jrnlWrite()`, `jrnlTruncate()`, `jrnlSync()`, and `jrnlFileSize()` dispatch either to the real file or the buffer. `sqlite3JournalOpen()`, `sqlite3JournalCreate()`, and `sqlite3JournalSize()` are the external hooks used by pager code.

`MemJournal` is also a `sqlite3_file` subclass. It stores rollback journal bytes in a linked list of `FileChunk` blocks and keeps `FilePoint` cursors for end-of-file and sequential read optimization. `memjrnlRead()` walks/caches chunk positions, `memjrnlWrite()` only appends and allocates chunks, `memjrnlTruncate()` frees all chunks and reopens the handle, and `sqlite3MemJournalOpen()`, `sqlite3IsMemJournal()`, and `sqlite3MemJournalSize()` expose the implementation.

### Walker and Name Resolution

`sqlite3WalkExpr()`, `sqlite3WalkExprList()`, `sqlite3WalkSelectExpr()`, `sqlite3WalkSelectFrom()`, and `sqlite3WalkSelect()` implement the `Walker` callback protocol with `WRC_Continue`, `WRC_Prune`, and `WRC_Abort`.

Resolution is centered on:

- `lookupName()`: resolves `Z`, `Y.Z`, or `X.Y.Z` against `NameContext` source lists, trigger `old`/`new` pseudo-tables, rowid aliases, and result-set aliases. It sets `Expr` fields such as `op`, `iDb`, `iTable`, `iColumn`, `pTab`, affinity, `colUsed`, and authorization read state.
- `resolveExprStep()`: walker callback for identifiers, dotted names, functions, aggregates, subqueries, `IN`, and CHECK-constraint restrictions.
- `resolveSelectStep()`: resolves SELECT result expressions, FROM subqueries, WHERE/HAVING, GROUP BY, ORDER BY, LIMIT/OFFSET, aggregate flags, and compound SELECT ordering.
- `sqlite3ResolveExprNames()` and `sqlite3ResolveSelectNames()`: public resolver entry points for expression trees and SELECT trees.

Alias handling is intentionally nuanced: non-column aliases may be wrapped in `TK_AS` so they are evaluated once for alias reuse, but GROUP BY suppresses that behavior, preserving older SQLite semantics where expressions such as `random()` can be evaluated separately.

### Expression Analysis and Code Generation

This chunk includes many expression helpers:

- Affinity/collation: `sqlite3ExprAffinity()`, `sqlite3ExprSetColl()`, `sqlite3ExprSetCollByToken()`, `sqlite3ExprCollSeq()`, `sqlite3CompareAffinity()`, `sqlite3IndexAffinityOk()`, `sqlite3BinaryCompareCollSeq()`, and `codeCompare()`.
- Expression lifetime: `sqlite3ExprAlloc()`, `sqlite3Expr()`, `sqlite3ExprAttachSubtrees()`, `sqlite3PExpr()`, `sqlite3ExprAnd()`, `sqlite3ExprFunction()`, `sqlite3ExprAssignVarNumber()`, `sqlite3ExprDelete()`, reduced/tree duplication helpers, `sqlite3ExprDup()`, `sqlite3ExprListDup()`, `sqlite3SrcListDup()`, `sqlite3IdListDup()`, `sqlite3SelectDup()`, `sqlite3ExprListAppend()`, name/span setters, length checks, and `sqlite3ExprListDelete()`.
- Constant and nullability checks: `sqlite3ExprIsConstant()`, `sqlite3ExprIsConstantNotJoin()`, `sqlite3ExprIsConstantOrFunction()`, `sqlite3ExprIsInteger()`, `sqlite3ExprCanBeNull()`, `sqlite3ExprCodeIsNullJump()`, and `sqlite3ExprNeedsNoAffinityChange()`.
- `IN`/subquery paths: `isCandidateForInOpt()`, `sqlite3FindInIndex()`, `sqlite3CodeSubselect()`, and `sqlite3ExprCodeIN()` choose existing rowid/index cursors where safe or build ephemeral tables and handle RHS NULL tracking.
- Codegen: `sqlite3ExprCodeTarget()`, `sqlite3ExprCodeTemp()`, `sqlite3ExprCode()`, `sqlite3ExprCodeAndCache()`, `sqlite3ExprCodeConstants()`, `sqlite3ExprCodeExprList()`, `sqlite3ExprIfTrue()`, and `sqlite3ExprIfFalse()` emit VDBE bytecode for literals, columns, variables, functions, CASE, BETWEEN, trigger references, `RAISE()`, subqueries, and boolean jumps.
- Comparison/aggregate analysis: `sqlite3ExprCompare()`, `sqlite3ExprListCompare()`, `sqlite3ExprAnalyzeAggregates()`, and `sqlite3ExprAnalyzeAggList()` identify equivalent expressions, aggregate columns, aggregate functions, DISTINCT aggregate cursors, and sorter columns.
- Register management: `sqlite3GetTempReg()`, `sqlite3ReleaseTempReg()`, `sqlite3GetTempRange()`, and `sqlite3ReleaseTempRange()` manage temporary VDBE registers while respecting the column cache.

### ALTER TABLE

`alter.c` registers built-in SQL helper functions through `sqlite3AlterFunctions()`:

- `sqlite_rename_table()` rewrites table names in CREATE TABLE/INDEX SQL.
- `sqlite_rename_trigger()` rewrites the target table in CREATE TRIGGER SQL.
- `sqlite_rename_parent()` rewrites parent table references in foreign-key clauses.

`sqlite3AlterRenameTable()` validates the target, rejects system tables/views and conflicting names, invokes virtual-table `xRename()` when present, rewrites rows in `sqlite_master` and `sqlite_temp_master`, updates `sqlite_sequence`, rewrites affected foreign-key child CREATE TABLE SQL when foreign keys are enabled, changes schema cookies, and reloads affected schema objects.

`sqlite3AlterBeginAddColumn()` creates a temporary `Table` copy prefixed with `sqlite_altertab_` for parser mutation. `sqlite3AlterFinishAddColumn()` validates ADD COLUMN restrictions, verifies constant defaults, rewrites the CREATE TABLE SQL text, raises the minimum file format to 2 or 3 depending on the default, and reloads the schema.

### ANALYZE

The covered start of `analyze.c` includes:

- `openStatTable()`: creates or clears `sqlite_stat1` and optionally `sqlite_stat2`, opens them for writing, and deletes rows for a single table when requested.
- `analyzeOneTable()`: skips views, virtual tables, and system tables; scans each index; counts total rows and distinct prefixes; optionally records `SQLITE_INDEX_SAMPLES` stat2 samples; writes `sqlite_stat1` rows; and emits table-only row-count stats for unindexed tables.
- `loadAnalysis()`, `analyzeDatabase()`, `analyzeTable()`, and `sqlite3Analyze()`: route the SQL `ANALYZE` forms across all databases, one database, or one table.
- `analysisLoader()`: parses sqlite_stat1 strings back into `Table.nRowEst` and `Index.aiRowEst`.
- `sqlite3DeleteIndexSamples()`: frees stat2 sample memory when enabled.
- Start of `sqlite3AnalysisLoad()`: clears prior index estimates and stat2 samples before reading sqlite_stat tables.

## Control Flow

The VDBE tail is runtime switch-dispatch code. It calls external module or b-tree APIs, sets `rc`, and exits through common halt labels. The important invariant is that all exits leave b-tree mutex arrays via `sqlite3BtreeMutexArrayLeave()`.

Incremental BLOB control flow is statement-backed. `sqlite3_blob_open()` builds a VDBE program and calls `blobSeekToRow()`. Once `OP_ResultRow` has positioned the VDBE cursor, read/write calls bypass SQL evaluation and operate directly on the borrowed b-tree cursor. If the row disappears, the value has a non-BLOB/TEXT type, an out-of-range request occurs, or b-tree returns `SQLITE_ABORT`, the handle is either rejected or invalidated so later operations fail predictably.

Journal control flow is delegated through `sqlite3_io_methods`. Lazy journals remain memory-only until a write exceeds `nBuf` or `sqlite3JournalCreate()` forces creation. Memory journals are append-only except for truncate-to-zero, which frees all chunks.

Resolver control flow is a top-down tree walk. Name contexts chain from inner to outer SELECTs; a successful match prunes the subtree after rewriting the expression node. SELECT resolution expands unresolved subqueries when needed, resolves result columns before WHERE/HAVING alias references, and handles compound ORDER BY only after all terms are resolved.

Expression codegen control flow emits VDBE jumps rather than computing every boolean into a register. `sqlite3ExprIfTrue()` and `sqlite3ExprIfFalse()` use short-circuit labels for AND/OR/NOT, direct comparison opcodes for relational operators, and special handling for NULL-sensitive `IS`, `IS NOT`, `BETWEEN`, and `IN`. Subquery and `IN` code may be guarded by a one-time `OP_If` unless correlated, trigger-dependent, or variable-containing.

ALTER and ANALYZE do not directly mutate all state in C. They generate nested SQL and VDBE programs that perform schema table updates, stat table writes, schema cookie changes, schema reparsing, and planner-stat reloads at statement execution time.

## State and Persistence Behavior

Persistent database state touched by this chunk includes:

- Rollback journals and memory journals, via pager-facing `sqlite3_file` implementations.
- Table row payload bytes modified by `sqlite3_blob_write()` through `sqlite3BtreePutData()`.
- `sqlite_master`/`sqlite_temp_master` SQL text, table names, index names, trigger metadata, and `sqlite_sequence` rows during ALTER TABLE.
- Database header file-format cookies during ADD COLUMN.
- `sqlite_stat1` and optional `sqlite_stat2` contents during ANALYZE.
- In-memory schema and planner state, including dropped/reparsed table/trigger definitions, `Table.nRowEst`, `Index.aiRowEst`, and optional `Index.aSample`.

Important transient state includes VDBE registers, expression flags (`EP_Resolved`, `EP_Agg`, `EP_xIsSelect`, `EP_IntValue`, `EP_Reduced`, `EP_TokenOnly`, `EP_Static`, `EP_FixedDest`), column-cache entries, parse counters (`nTab`, `nMem`, `nVar`, alias counters), name-context aggregate/reference counters, trigger old/new bitmasks, and incremental BLOB cursor state.

## Dependencies and Integration Points

This code depends heavily on internal SQLite layers:

- VDBE opcodes and builders (`sqlite3VdbeAddOp*`, `sqlite3VdbeChange*`, labels, P4 ownership modes).
- B-tree and pager APIs for page count, cursor data, blob writes, table/index opens, locks, schema cookies, and journal use.
- VFS APIs via `sqlite3_file`, `sqlite3_io_methods`, and `sqlite3Os*` wrappers.
- Parser structures (`Parse`, `Expr`, `ExprList`, `Select`, `SrcList`, `NameContext`, `AggInfo`, `Table`, `Index`, `FKey`, `Trigger`).
- Schema, authorization, virtual table, foreign-key, trigger, collation, function registry, and memory allocation helpers.

FoundationDB integration risk is mostly indirect: this vendored SQLite amalgamation defines SQL semantics and pager behavior used by the FoundationDB SQLite layer. Any local changes to VFS, pager, b-tree, virtual table modules, or tests around SQL compatibility can surface through these code paths.

## Risks

- Incremental BLOB handles rely on a live VDBE statement and borrowed b-tree cursor. Incorrect finalization, cursor invalidation, or mutex handling can cause stale cursor access, aborted handles, or lock-order bugs.
- Writable blob handles deliberately reject indexed and foreign-key child columns. Relaxing this would bypass constraint/index maintenance because writes mutate payload bytes directly.
- `blobReadWrite()` bounds checks use `iOffset+n`; integer overflow or signedness mistakes would be high impact for memory safety, though this implementation uses SQLite's established integer assumptions.
- Lazy journal materialization must preserve all bytes already written before switching to the real file. Errors in `createFile()` or offset handling can break rollback durability.
- `memjrnlRead()` assumes SQLite never reads past journal EOF and asserts append-only writes. External use outside pager assumptions would be unsafe.
- Name resolution changes can silently alter SQL semantics, especially alias visibility, NATURAL/USING duplicate suppression, trigger `old`/`new`, rowid aliases, aggregate misuse detection, and compound ORDER BY matching.
- Expression duplication/deletion uses reduced/token-only/static flags and mixed inline/allocated token storage. Incorrect flag propagation can cause leaks, double frees, or use-after-free.
- `IN` optimization depends on affinity, collation, uniqueness, nullability, and correlation checks. Choosing an existing index incorrectly can produce wrong answers, especially with NULL-sensitive `IN` semantics.
- Boolean codegen assumes token constants align with VDBE opcode constants for comparison operators. Any opcode renumbering must preserve the asserted relationships.
- ALTER TABLE rewrites raw CREATE SQL text using token scanning. Quoting, unusual whitespace, triggers, foreign-key references, and temp triggers are compatibility-sensitive.
- ANALYZE statistics are planner inputs. Bad distinct-count math, stat-table schema handling, collation use, or stat loading can produce poor or incorrect query plans.
- The chunk ends before `sqlite3AnalysisLoad()` completes, so stat1/stat2 readback behavior must be reconciled with the next chunk before drawing full conclusions about planner-stat loading.

## Test and Validation Signals

Useful validation signals for this range include:

- SQLite core tests for incremental blob APIs: open/read/write/bytes/reopen/close, nonexistent rowid, non-BLOB/TEXT columns, schema invalidation, writable indexed columns, foreign-key child columns, and concurrent row changes.
- Pager/journal tests across rollback modes, `journal_mode=MEMORY`, atomic-write VFS behavior, forced journal creation, short reads, truncation, sync, and OOM during chunk allocation.
- Resolver tests for ambiguous columns, aliases in WHERE/ORDER/GROUP, compound SELECT ORDER BY, subquery correlation, CHECK constraint restrictions, aggregate misuse, HAVING without GROUP BY, trigger `old`/`new`, rowid aliases, and authorization callbacks.
- Expression-codegen tests for affinity/collation comparisons, `IN` with lists/subqueries/NULLs, rowid and index-backed `IN`, correlated subqueries, EXISTS/scalar SELECT, CASE, BETWEEN, COALESCE/IFNULL short-circuiting, virtual-table function overloading, RAISE in and out of triggers, and expression-depth limits.
- ALTER TABLE tests for renaming tables with indexes, triggers, temp triggers, autoincrement sequence rows, virtual tables with/without `xRename`, foreign-key parent references, quoted identifiers, reserved/system names, views, and ADD COLUMN constraints/defaults/file-format behavior.
- ANALYZE tests for creating/clearing stat tables, per-table and per-database analyze forms, unindexed tables, multi-column index statistics, stat2 sample generation when enabled, authorization, system-table skipping, OOM paths, and subsequent query-plan changes after `OP_LoadAnalysis`.
- Build matrix coverage with feature flags such as `SQLITE_OMIT_INCRBLOB`, `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_ALTERTABLE`, `SQLITE_OMIT_ANALYZE`, and `SQLITE_ENABLE_STAT2`.

### subset-b-008414: lines 60570-68379

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 60570-68379

## Chunk Scope

This chunk is a wide band of SQLite amalgamation code embedded under the FoundationDB storage-engine tree. It starts at the end of `analyze.c` statistics loading, covers complete embedded sections for `attach.c`, `auth.c`, `build.c`, `callback.c`, `delete.c`, and `func.c`, and ends part-way into `fkey.c` at the beginning of `fkScanChildren()`.

The source is not FoundationDB-specific glue in this range. It is SQLite core implementation code: parser actions, schema metadata management, SQL function registration, DELETE code generation, ATTACH/DETACH, authorizer hooks, collation/function lookup, and the start of foreign-key enforcement code.

## Purpose

The code in this chunk turns parsed SQL syntax into SQLite runtime state and VDBE bytecode. Its main responsibilities are:

- loading planner statistics from `sqlite_stat1` and optional `sqlite_stat2`;
- implementing `ATTACH`/`DETACH` and the database-name fixer used by views, triggers, and indexes;
- enforcing `sqlite3_set_authorizer()` decisions during parse/code generation;
- creating, dropping, and maintaining schema objects such as tables, views, indexes, foreign-key declarations, source lists, and transactions;
- maintaining in-memory schema hashes, table/index reference lifetimes, schema cookies, and shared-cache table locks;
- implementing DELETE statement code generation, row deletion, index-key deletion, and trigger/foreign-key hooks;
- defining SQLite built-in scalar and aggregate SQL functions and registering LIKE/GLOB optimization metadata;
- resolving parent indexes and generating early VDBE checks for foreign-key constraints.

## Important APIs, Types, And Functions

### Statistics Loading

- The opening tail of the `ANALYZE` implementation checks for `sqlite_stat1`, executes `SELECT tbl, idx, stat FROM %Q.sqlite_stat1`, and passes rows to `analysisLoader`.
- Under `SQLITE_ENABLE_STAT2`, it loads samples from `sqlite_stat2` into `Index.aSample`, allocating `SQLITE_INDEX_SAMPLES` `IndexSample` slots per index. Numeric samples store `u.r`; text/blob samples store up to 24 bytes.

### ATTACH, DETACH, And Database Fixing

- `resolveAttachExpr()` treats bare identifiers at the root of ATTACH/DETACH expressions as string literals and rejects non-constant resolved expressions.
- `attachFunc()` is the runtime SQL function behind compiled `ATTACH`. It validates attached database limits, autocommit state, duplicate database names, opens a Btree with `sqlite3BtreeOpen()`, obtains schema with `sqlite3SchemaGet()`, checks text encoding compatibility, applies locking/secure-delete settings, optionally attaches codec keys, initializes schema with `sqlite3Init()`, and rolls back the new `Db` entry on failure.
- `detachFunc()` validates that the named database exists, is not `main` or `temp`, is not inside a transaction, and has no active read transaction or backup before closing the Btree and resetting internal schema.
- `codeAttach()`, `sqlite3Attach()`, and `sqlite3Detach()` compile SQL syntax into an `OP_Function` call to the internal `sqlite_attach` or `sqlite_detach` function, followed by `OP_Expire`.
- `sqlite3FixInit()`, `sqlite3FixSrcList()`, `sqlite3FixSelect()`, `sqlite3FixExpr()`, `sqlite3FixExprList()`, and `sqlite3FixTriggerStep()` enforce that non-TEMP views, triggers, and indexes do not reference objects in other databases.

### Authorization

- `sqlite3_set_authorizer()` installs or clears the connection authorizer callback and expires prepared statements.
- `sqlite3AuthReadCol()` invokes `xAuth` for `SQLITE_READ`; `SQLITE_DENY` records an auth error, while malformed return codes become "authorizer malfunction".
- `sqlite3AuthRead()` maps a `TK_COLUMN` or trigger pseudo-column expression to a table/column name and converts it to `TK_NULL` when the authorizer returns `SQLITE_IGNORE`.
- `sqlite3AuthCheck()` is the general parse-time authorization gate for CREATE/DROP/INSERT/DELETE/TRANSACTION/SAVEPOINT/etc. It is skipped during schema initialization and inside `sqlite3_declare_vtab`.
- `sqlite3AuthContextPush()` and `sqlite3AuthContextPop()` track view/trigger context passed to the authorizer.

### Schema Build And Parser Actions

- `sqlite3BeginParse()` initializes parse flags for a new statement.
- `sqlite3TableLock()` and `codeTableLocks()` record and emit shared-cache `OP_TableLock` requirements.
- `sqlite3FinishCoding()` finalizes a statement VDBE: emits `OP_Halt`, fills the deferred schema-cookie/transaction prologue, starts virtual table transactions, emits table locks, starts AUTOINCREMENT tracking, jumps back to executable code, and calls `sqlite3VdbeMakeReady()`.
- `sqlite3NestedParse()` recursively parses generated SQL used for schema changes, preserving the outer parse state.
- Lookup and lifetime APIs include `sqlite3FindTable()`, `sqlite3LocateTable()`, `sqlite3FindIndex()`, `sqlite3UnlinkAndDeleteIndex()`, `sqlite3ResetInternalSchema()`, `sqlite3CommitInternalChanges()`, `sqlite3DeleteTable()`, and `sqlite3UnlinkAndDeleteTable()`.
- Name/schema helpers include `sqlite3NameFromToken()`, `sqlite3OpenMasterTable()`, `sqlite3FindDbName()`, `sqlite3FindDb()`, `sqlite3TwoPartName()`, and `sqlite3CheckObjectName()`.
- CREATE TABLE/VIEW helpers include `sqlite3StartTable()`, `sqlite3AddColumn()`, `sqlite3AddNotNull()`, `sqlite3AffinityType()`, `sqlite3AddColumnType()`, `sqlite3AddDefaultValue()`, `sqlite3AddPrimaryKey()`, `sqlite3AddCheckConstraint()`, `sqlite3AddCollateType()`, `sqlite3ChangeCookie()`, `createTableStmt()`, `sqlite3EndTable()`, `sqlite3CreateView()`, and `sqlite3ViewGetColumnNames()`.
- Drop and storage-maintenance helpers include `sqliteViewResetAll()`, `sqlite3RootPageMoved()`, `destroyRootPage()`, `destroyTable()`, and `sqlite3DropTable()`.
- Foreign-key declaration parser actions in this chunk are `sqlite3CreateForeignKey()` and `sqlite3DeferForeignKey()`.
- Index and source-list helpers include `sqlite3RefillIndex()`, `sqlite3CreateIndex()`, `sqlite3DefaultRowEst()`, `sqlite3DropIndex()`, `sqlite3ArrayAllocate()`, `sqlite3IdListAppend()`, `sqlite3IdListDelete()`, `sqlite3IdListIndex()`, `sqlite3SrcListEnlarge()`, `sqlite3SrcListAppend()`, `sqlite3SrcListAssignCursors()`, `sqlite3SrcListDelete()`, `sqlite3SrcListAppendFromTerm()`, `sqlite3SrcListIndexedBy()`, and `sqlite3SrcListShiftJoinType()`.
- Transaction/codegen helpers include `sqlite3BeginTransaction()`, `sqlite3CommitTransaction()`, `sqlite3RollbackTransaction()`, `sqlite3Savepoint()`, `sqlite3OpenTempDatabase()`, `sqlite3CodeVerifySchema()`, `sqlite3BeginWriteOperation()`, `sqlite3MultiWrite()`, `sqlite3MayAbort()`, `sqlite3HaltConstraint()`, `sqlite3Reindex()`, and `sqlite3IndexKeyinfo()`.

### Collations, Functions, And Schema Allocation

- `sqlite3GetCollSeq()`, `sqlite3FindCollSeq()`, and `sqlite3CheckCollSeq()` resolve collations, call collation-needed callbacks, synthesize missing encodings where possible, and report unresolved collations.
- `sqlite3FuncDefInsert()` and `sqlite3FindFunction()` manage per-connection and global function-definition hash tables, including preferred encoding and arity matching.
- `sqlite3SchemaFree()` clears schema hash tables and deletes triggers, tables, indexes, and foreign-key hash content. `sqlite3SchemaGet()` obtains or initializes a `Schema` associated with a Btree.

### DELETE Code Generation

- `sqlite3SrcListLookup()` resolves the target table in a one-entry source list.
- `sqlite3IsReadOnly()` rejects writes to virtual tables without `xUpdate`, protected system tables without writable-schema mode, and views when triggers are not allowed.
- `sqlite3MaterializeView()` realizes a view into an ephemeral table for INSTEAD OF trigger processing.
- `sqlite3LimitWhere()` rewrites limited DELETE/UPDATE syntax into a `rowid IN (SELECT rowid ... ORDER BY ... LIMIT/OFFSET ...)` expression when enabled.
- `sqlite3DeleteFrom()` compiles DELETE: resolves target, checks triggers/views/read-only/auth, assigns cursors, optionally uses truncate optimization, otherwise collects rowids in a RowSet, opens write cursors, deletes rows, fires triggers, handles virtual tables, updates AUTOINCREMENT, and optionally returns a row count.
- `sqlite3GenerateRowDelete()` handles a single row delete with BEFORE/AFTER triggers, OLD register population, foreign-key checks/actions, index deletion, table row deletion, and skip labels for trigger-side row removal or `RAISE(IGNORE)`.
- `sqlite3GenerateRowIndexDelete()` and `sqlite3GenerateIndexKey()` build and delete index keys for the current table row.

### Built-In SQL Functions

The `func.c` section defines scalar functions such as `min/max` scalar variants, `typeof`, `length`, `abs`, `substr`, `round`, `upper`, `lower`, `random`, `randomblob`, `last_insert_rowid`, `changes`, `total_changes`, `like`, `glob`, `nullif`, `sqlite_version`, `sqlite_source_id`, compile-option diagnostics, `quote`, `hex`, `zeroblob`, `replace`, `trim/ltrim/rtrim`, optional `soundex`, and optional `load_extension`.

Aggregate state is implemented by `SumCtx` for `sum`, `total`, and `avg`, `CountCtx` for `count`, a `Mem` aggregate accumulator for aggregate `min/max`, and `StrAccum` for `group_concat`.

Registration functions are `sqlite3RegisterBuiltinFunctions()`, `sqlite3RegisterLikeFunctions()`, `sqlite3IsLikeFunction()`, and `sqlite3RegisterGlobalFunctions()`.

### Foreign-Key Enforcement Start

- `locateFkeyIndex()` finds the required parent key for a foreign key. It accepts a single-column INTEGER PRIMARY KEY parent without an index, otherwise requires a UNIQUE/PRIMARY KEY index with matching columns and default column collations. For composite keys it may allocate an `aiCol` map from parent-index order to child-column indexes.
- `fkLookupParent()` emits VDBE code for child-side INSERT/DELETE/UPDATE checks. It skips checks for NULL child key columns, looks up parent rows by rowid or unique index, handles self-referential insert matches, and either halts immediately for simple immediate single-row inserts or adjusts `OP_FkCounter`.
- `fkScanChildren()` begins parent-side scan code generation for DELETE/UPDATE checks and deferred insert resolution. This chunk ends while it is building and resolving the WHERE expression matching child rows to the parent key.

## Control Flow

ATTACH flow is parse-time compilation plus runtime execution. The parser calls `sqlite3Attach()` or `sqlite3Detach()`, which delegates to `codeAttach()`. `codeAttach()` resolves constant expressions, runs authorization, materializes function arguments into registers, emits `OP_Function`, and expires statements. At runtime, `attachFunc()` mutates `db->aDb` and opens/initializes the new Btree/schema; `detachFunc()` closes and removes a database after lock and transaction checks.

Schema creation flows through parser actions. `sqlite3StartTable()` resolves the target database, checks authorization and namespace collisions, allocates a `Table`, and reserves a placeholder row in `sqlite_master` when not initializing. Column/constraint helpers mutate `pParse->pNewTable`. `sqlite3EndTable()` resolves CHECK constraints, creates/populates CTAS output if needed, updates the placeholder `sqlite_master` row with final SQL text, bumps the schema cookie, creates `sqlite_sequence` if needed, schedules schema reparse, or inserts the table directly into in-memory hashes during initialization.

Index creation follows a similar two-mode path. `sqlite3CreateIndex()` resolves table and database names, blocks system/view/virtual-table indexing, derives or invents an index name, authorizes the operation, builds an `Index` object with column mappings/collations/sort order, suppresses duplicate automatic constraints, inserts initialization-time indexes into schema hashes, or emits VDBE to create/refill/persist a new index and parse the schema. `sqlite3DropIndex()` deletes `sqlite_master` and `sqlite_stat1` rows, changes the schema cookie, destroys the root page, and emits `OP_DropIndex`.

DROP TABLE resolves the object, checks type compatibility (`DROP TABLE` vs `DROP VIEW`), authorizes deletes from schema and table, rejects `sqlite_` system tables, begins a write operation, drops triggers, foreign-key side effects, AUTOINCREMENT rows, master-table entries, optional analyze stats, table/index root pages, virtual-table storage, schema cookies, and in-memory view column caches.

DELETE compilation first resolves the target table/view and associated triggers. It uses a fast `OP_Clear` path only when there is no WHERE clause, no triggers, no virtual table, and no required foreign-key work. Otherwise it scans matching rows into a RowSet, then performs row deletes after the scan to avoid changing scan order. Per-row deletion calls trigger and foreign-key code around physical index/table deletion.

Built-in function flow is callback-based. Scalar functions inspect `sqlite3_value` arguments and return via `sqlite3_result_*`. Aggregate steps allocate state with `sqlite3_aggregate_context()` and finalizers produce the final result. Function lookup uses hash buckets keyed by case-folded first character plus name length, then scores arity and encoding compatibility.

Foreign-key flow starts by validating the parent key with `locateFkeyIndex()`. Child-row changes use `fkLookupParent()` to find the referenced parent or adjust immediate/deferred counters. Parent-row changes use `fkScanChildren()` to generate a WHERE scan over child rows that reference the old/new parent key.

## State And Persistence Behavior

Persistent database state touched by this chunk includes:

- attached database files and their Btree/Pager handles;
- `sqlite_master` / `sqlite_temp_master` records for tables, views, indexes, triggers, and schema SQL text;
- table and index root pages created, cleared, destroyed, or moved by auto-vacuum;
- `sqlite_sequence` rows for AUTOINCREMENT tables;
- `sqlite_stat1` rows and optional `sqlite_stat2` samples;
- schema cookies (`BTREE_SCHEMA_VERSION`), file format cookies, and text-encoding cookies.

Important in-memory state includes:

- `sqlite3.aDb[]`, including dynamic expansion beyond `aDbStatic` and compaction after detach/reset;
- `Schema` hash tables for tables, indexes, triggers, and foreign keys;
- `Table`, `Column`, `Index`, `FKey`, `FuncDef`, `CollSeq`, `KeyInfo`, `SrcList`, `IdList`, `Expr`, `Select`, and `Vdbe` structures;
- parse flags such as `cookieMask`, `writeMask`, `isMultiWrite`, `mayAbort`, `nTab`, `nMem`, `pNewTable`, and authorization context;
- per-statement and deferred foreign-key counters stored in VDBE/database state;
- aggregate contexts and function result buffers for SQL functions.

The code is careful to distinguish initialization (`db->init.busy`) from user-issued DDL. During schema loading it avoids writing disk state and instead populates in-memory hashes from existing `sqlite_master` rows. During user DDL it emits VDBE bytecode to update persistent schema tables, then schedules schema reparse and expires prepared statements where needed.

Memory ownership is explicit and local. Most parser helper APIs consume token-derived strings or expression/source-list objects and clean them on exit. Several structures pack variable-length arrays and strings into one allocation (`Index`, `FKey`, `KeyInfo`). OOM generally sets `db->mallocFailed` and propagates `SQLITE_NOMEM` or parse errors.

## Dependencies And Integration Points

This chunk integrates with most core SQLite subsystems:

- Btree/Pager: `sqlite3BtreeOpen`, `sqlite3BtreeClose`, `sqlite3BtreePager`, `sqlite3BtreeSecureDelete`, `sqlite3BtreeSchema`, `sqlite3BtreeSetPageSize`, root-page creation/destruction, schema cookies.
- VDBE: emits opcodes including `OP_Function`, `OP_Expire`, `OP_TableLock`, `OP_Halt`, `OP_Transaction`, `OP_VerifyCookie`, `OP_VBegin`, `OP_OpenWrite`, `OP_CreateTable`, `OP_CreateIndex`, `OP_Insert`, `OP_ParseSchema`, `OP_Destroy`, `OP_DropTable`, `OP_DropIndex`, `OP_Clear`, `OP_RowSetAdd`, `OP_RowSetRead`, `OP_Delete`, `OP_IdxDelete`, `OP_FkCounter`, and `OP_FkIfZero`.
- Parser/name resolver: `Parse`, `NameContext`, `Expr`, `ExprList`, `Select`, `SrcList`, token dequoting, expression resolution, and nested parser entry.
- Authorization: all DDL, transaction, savepoint, read-column, and DELETE paths can invoke the user authorizer.
- Virtual tables: CREATE/DROP and read-only checks use `sqlite3VtabCallConnect`, `sqlite3GetVTable`, `OP_VBegin`, `OP_VDestroy`, and `OP_VUpdate`.
- Triggers/views: view column derivation, view materialization, trigger-list lookup, trigger execution, and trigger old-row masks.
- Foreign keys: declaration storage in `Schema.fkeyHash`, parent lookup/index validation, child/parent scan code generation, and delete/drop-table integration.
- Collations/functions: collation-needed callbacks, global and per-connection function hash tables, LIKE optimizer flags, date/time and ALTER TABLE function registration.
- Optional compile-time features: `SQLITE_OMIT_ATTACH`, `SQLITE_OMIT_AUTHORIZATION`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_ENABLE_STAT2`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_REINDEX`, `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, `SQLITE_SOUNDEX`, `SQLITE_OMIT_LOAD_EXTENSION`, and `SQLITE_HAS_CODEC`.

## Risks And Edge Cases

- ATTACH/DETACH mutates `db->aDb` and global schema state. Failure cleanup must close partially opened Btrees, reset schema hashes, preserve `main`/`temp`, restore `nDb`, and avoid leaking `zName`; regressions here can leave corrupt connection-local schema state.
- ATTACH is forbidden inside explicit transactions and requires attached database encodings to match. Codec key handling adds a security-sensitive extension point when encryption is enabled.
- `sqlite3ResetInternalSchema(db, 0)` frees all schema hashes and compacts closed attached DB slots. Callers must hold Btree mutexes as asserted; misuse risks stale `Table`/`Index` pointers.
- Schema cookie logic is central to prepared statement invalidation. Missing `sqlite3ChangeCookie()` or `OP_Expire` after DDL can allow stale query plans or stale schema reads.
- `sqlite3NestedParse()` generates SQL strings that mutate `sqlite_master`; quoting and `%Q` usage are security- and correctness-relevant.
- Object-name restrictions around `sqlite_` are intentionally bypassed during initialization, nested parse, or writable-schema mode. This is a privileged path and can corrupt internal tables if misused.
- Index creation deliberately allows duplicate indexed columns for backward compatibility, but only the first instance is useful to the optimizer. This can surprise callers and is called out by a TODO.
- Automatic index de-duplication ignores sort-order differences when comparing equivalent UNIQUE/PRIMARY KEY constraints but respects collation and column order.
- DELETE truncate optimization is bypassed when triggers, virtual tables, or foreign keys are involved. An incorrect `sqlite3FkRequired()` result could silently skip required FK processing.
- Trigger and FK delete paths depend on OLD register masks. Missing a required old column can make triggers or FK actions read wrong/default data.
- LIKE/GLOB matching can be quadratic and recursive; `likeFunc()` enforces `SQLITE_LIMIT_LIKE_PATTERN_LENGTH` to limit abuse.
- `replace`, `quote`, `hex`, `zeroblob`, `group_concat`, and `randomblob` all enforce or rely on length limits. Integer overflow and allocation checks are important for hostile SQL inputs.
- Aggregate `sum()` tracks integer overflow only while all inputs are integer-like; once approximate inputs appear, result semantics change to floating point.
- Foreign-key parent lookup requires parent unique indexes to use default collations for explicit parent columns. Non-default collations can produce "foreign key mismatch" even when a unique index exists.
- The chunk ends in the middle of `fkScanChildren()`, so parent-side FK scan resolution and action emission continue in the next chunk.

## Test Signals

Useful behavioral tests for this chunk include:

- ATTACH/DETACH: attach duplicate names, too many databases, attach inside transaction, detach `main`/`temp`, detach locked/read-transaction/backup databases, attach encoding mismatch, and schema-init failure cleanup.
- Authorization: callbacks returning `SQLITE_OK`, `SQLITE_DENY`, `SQLITE_IGNORE`, and invalid codes for read columns, DDL, DELETE, transactions, and savepoints.
- DDL/schema: CREATE TABLE with duplicate columns, too many columns, invalid defaults, multiple primary keys, AUTOINCREMENT on non-INTEGER PK, CHECK name resolution, reserved `sqlite_` names, CREATE VIEW with parameters, circular view column derivation, DROP TABLE vs DROP VIEW mismatch, and writable-schema/system-table protection.
- Indexes: explicit index name collisions with tables/indexes, missing columns, collation lookup failure, UNIQUE conflict clause conflicts, automatic index de-duplication, DROP automatic index rejection, REINDEX by database/table/index/collation, and `sqlite_stat1` cleanup.
- Source lists and transactions: malformed `ON`/`USING` without JOIN, `INDEXED BY`/`NOT INDEXED`, temp database open failures, schema-cookie verification, BEGIN/COMMIT/ROLLBACK/SAVEPOINT authorizer behavior.
- DELETE: fast truncate vs row-by-row delete, count-changes result row, DELETE from views with INSTEAD OF triggers, virtual-table delete through `xUpdate`, BEFORE trigger deleting the same row, AFTER triggers, index-entry removal, limited DELETE rewrite, and FK-required bypass of truncate.
- Functions: NULL behavior for scalar functions, UTF-8 length/substr/trim cases, LIKE/GLOB escape validation and pattern length limits, abs integer overflow, random minimum bound, zeroblob/hex/quote length limits, replace growth/OOM, load-extension errors, aggregate empty-input behavior, sum overflow, min/max collation behavior, and group-concat separator behavior.
- Foreign keys: parent INTEGER PRIMARY KEY match, composite parent unique index match, missing parent key, wrong parent key cardinality, non-default parent collation mismatch, NULL child-key satisfaction, self-referential insert, immediate single-row insert halt path, and deferred/immediate counter changes.

### subset-b-008415: lines 68380-75677

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 68380-75677

## Scope And Purpose

This chunk covers an amalgamated SQLite slice that crosses several logical source files: the tail of `fkey.c`, most of `insert.c`, `legacy.c`, `sqlite3ext.h` and `loadext.c`, most of `pragma.c`, `prepare.c`, and the beginning of `select.c`. It is parser/code-generator and public API glue rather than a single storage subsystem. The code translates SQL features into VDBE programs, manages schema initialization, exposes extension-loading interfaces, and implements legacy convenience APIs.

The opening foreign-key section completes enforcement and action generation for `INSERT`, `UPDATE`, `DELETE`, and `DROP TABLE`. The insert section builds the VDBE templates for `INSERT ... VALUES`, `INSERT ... SELECT`, autoincrement maintenance, constraint checking, index writes, trigger interaction, virtual-table insertion, and the raw-record transfer optimization. The legacy/extension sections implement `sqlite3_exec()`, the stable extension API dispatch table, runtime extension loading, and global auto-extension registration.

The pragma section handles a broad set of database, pager, schema, WAL, and debug settings. Some pragmas only read or flip connection flags; others emit transactional VDBE code that persists metadata into database headers or invokes pager/btree operations. The prepare section is the schema-loading and SQL compilation boundary: it loads `sqlite_master`, validates schema cookies, protects against schema locks, compiles SQL text, and supports automatic reprepare for `sqlite3_prepare_v2()` statements. The select section starts SELECT AST construction and early code generation helpers for joins, DISTINCT, ORDER BY, LIMIT/OFFSET, result destinations, and result column metadata.

## Important APIs, Types, And Functions

Foreign-key APIs in this range include `sqlite3FkReferences()`, `sqlite3FkDropTable()`, `sqlite3FkCheck()`, `sqlite3FkOldmask()`, `sqlite3FkRequired()`, `sqlite3FkActions()`, and `sqlite3FkDelete()`. The key local helper is `fkActionTrigger()`, which synthesizes cached `Trigger` structures for `ON DELETE` and `ON UPDATE` actions such as `CASCADE`, `SET NULL`, `SET DEFAULT`, and `RESTRICT`.

Insert code-generation entry points include `sqlite3OpenTable()`, `sqlite3IndexAffinityStr()`, `sqlite3TableAffinityStr()`, `sqlite3Insert()`, `sqlite3GenerateConstraintChecks()`, `sqlite3CompleteInsertion()`, and `sqlite3OpenTableAndIndices()`. Local helpers include `readsTable()` for detecting self-referential `INSERT ... SELECT`, autoincrement helpers `autoIncBegin()`, `sqlite3AutoincrementBegin()`, `autoIncStep()`, `sqlite3AutoincrementEnd()`, and transfer-optimization helpers `xferCompatibleCollation()`, `xferCompatibleIndex()`, and `xferOptimization()`.

The legacy public API is `sqlite3_exec()`. It loops over semicolon-separated SQL statements, prepares each statement, steps it, optionally materializes callback column names and text values, handles `SQLITE_SCHEMA` retry, finalizes statements, and returns an allocated error string through `pzErrMsg`.

The extension API surface is represented by `struct sqlite3_api_routines`, `SQLITE_EXTENSION_INIT1`, `SQLITE_EXTENSION_INIT2`, the `sqlite3Apis` dispatch table, `sqlite3_load_extension()`, `sqlite3_enable_load_extension()`, `sqlite3CloseExtensions()`, `sqlite3_auto_extension()`, `sqlite3_reset_auto_extension()`, and `sqlite3AutoLoadExtensions()`. The dispatch table preserves ABI compatibility by appending newer APIs after older entries and substituting `NULL` for compile-time omitted features.

Pragma helpers include `getSafetyLevel()`, `getBoolean()`, `getLockingMode()`, `getAutoVacuum()`, `getTempStore()`, `invalidateTempStorage()`, `changeTempStorage()`, `returnSingleInt()`, `flagPragma()`, `actionName()`, and `sqlite3JournalModename()`. The central entry point `sqlite3Pragma()` recognizes database-qualified pragmas, resolves the target database, normalizes string/numeric values, and either mutates connection state immediately or emits VDBE opcodes for runtime database work.

Schema and prepare functions include `corruptSchema()`, `sqlite3InitCallback()`, `sqlite3InitOne()`, `sqlite3Init()`, `sqlite3ReadSchema()`, `schemaIsValid()`, `sqlite3SchemaToIndex()`, `sqlite3Prepare()`, `sqlite3LockAndPrepare()`, `sqlite3Reprepare()`, `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3Prepare16()`, `sqlite3_prepare16()`, and `sqlite3_prepare16_v2()`.

SELECT helpers in this slice include `clearSelect()`, `sqlite3SelectDestInit()`, `sqlite3SelectNew()`, `sqlite3SelectDelete()`, `sqlite3JoinType()`, `columnIndex()`, `tableAndColumnIndex()`, `addWhereTerm()`, `setJoinExpr()`, `sqliteProcessJoin()`, `pushOntoSorter()`, `codeOffset()`, `codeDistinct()`, `checkForMultiColumnSelectError()`, `selectInnerLoop()`, `keyInfoFromExprList()`, `selectOpName()`, `explainTempTable()`, `explainComposite()`, `generateSortTail()`, `columnType()`, `generateColumnTypes()`, and `generateColumnNames()`.

Important structures touched here include `Parse`, `sqlite3`, `Vdbe`, `Table`, `Index`, `FKey`, `Trigger`, `TriggerStep`, `Select`, `SelectDest`, `Expr`, `ExprList`, `SrcList`, `IdList`, `Schema`, `Db`, `Btree`, `Pager`, `InitData`, `AutoincInfo`, `KeyInfo`, `CollSeq`, and `sqlite3_api_routines`.

## Control Flow

Foreign-key enforcement is split between child-table and parent-table checks. `sqlite3FkCheck()` first scans `pTab->pFKey` for constraints where the modified table is the child. It resolves the parent table and parent key index, requests authorization to read parent key columns when authorization is enabled, takes a table read lock, then calls `fkLookupParent()` with `-1` when deleting old child rows or `+1` when inserting new child rows. It then scans `sqlite3FkReferences(pTab)` for constraints where the modified table is the parent. Parent-row changes generate scans of child tables with `fkScanChildren()`, incrementing/decrementing foreign-key counters or raising immediate errors.

`sqlite3FkDropTable()` emits a trigger-disabled `DELETE FROM <table>` before schema removal when dropping a table could affect foreign keys. If the table is only a deferred child, it guards the DELETE with `OP_FkIfZero`; if the DELETE produces immediate FK violations, it halts before schema changes are made. `sqlite3FkActions()` walks referencing foreign keys, obtains or creates an action trigger with `fkActionTrigger()`, and emits row-trigger code for applicable update/delete actions.

`fkActionTrigger()` constructs a synthetic trigger body matching the foreign-key action. It builds `WHERE` terms comparing child columns to `old` parent key values, optional `WHEN` terms for update actions that actually changed parent key values, and either a child `DELETE`, child `UPDATE`, or `SELECT RAISE()` step. It temporarily disables lookaside because cached trigger objects must outlive the current parse allocation pattern. The resulting trigger is cached in `FKey.apTrigger[]` and later freed by `sqlite3FkDelete()`.

`sqlite3Insert()` begins by resolving the target table/view, checking authorization and read-only status, identifying triggers, allocating a VDBE, and starting a write operation. If the statement is `INSERT INTO dest SELECT * FROM src` and strict compatibility checks pass, `xferOptimization()` may copy raw table and index records directly. Otherwise, an AUTOINCREMENT register is allocated if needed.

For `INSERT ... SELECT`, `sqlite3Insert()` compiles the SELECT as a coroutine that writes each result row into destination registers and sets an EOF register when complete. If triggers exist or the SELECT reads the destination table, it materializes the coroutine output into an ephemeral table first. For `INSERT ... VALUES`, it resolves each expression directly. It then validates source column counts, resolves optional column lists, initializes row-count output if requested, opens target table and index cursors, and enters the insertion loop.

Inside the insertion loop, BEFORE triggers are fed a `NEW.*` register array. Rowid generation uses explicit primary-key values when present, `OP_NewRowid` when NULL or omitted, and `OP_MustBeInt` to enforce rowid type. Column registers are filled from the VALUES expressions, SELECT registers, temp table, or column defaults. The insert path then runs constraint checks, foreign-key checks, index record creation, table record insertion, AFTER triggers, row-count accounting, and loop continuation.

`sqlite3GenerateConstraintChecks()` enforces rowid uniqueness, NOT NULL, CHECK constraints, and UNIQUE/PRIMARY KEY index constraints. Conflict resolution considers per-column and per-index policies plus the statement-level `onError`. Depending on policy, it emits halt/constraint opcodes, skip jumps, delete-before-replace code, or index probes. `sqlite3CompleteInsertion()` emits the actual `OP_IdxInsert` operations for each index and either `OP_Insert` for ordinary btrees or `OP_VUpdate` for virtual tables.

The transfer optimization performs early syntactic checks, then semantic compatibility checks: no destination triggers or virtual tables, simple single-table `SELECT *`, no filters/grouping/sorting/limits/distinct/compound, different real source/destination tables, identical column count, matching integer primary key location, compatible affinities/collations, destination NOT NULL not weaker than source, compatible indexes, and compatible CHECK constraints. It then opens source/destination cursors, optionally verifies empty destination, copies `OP_RowData`/`OP_Insert` rows, copies compatible index keys with `OP_RowKey`/`OP_IdxInsert`, and falls back to the ordinary path if the destination-empty runtime check fails.

`sqlite3_exec()` is a public convenience loop over prepare/step/finalize. It skips comments/whitespace that do not produce statements, initializes callback column-name arrays on the first row or on a NULL-callback row, converts result values to UTF-8 text for callback delivery, stops with `SQLITE_ABORT` if the callback returns nonzero, retries once on schema changes, and copies `sqlite3_errmsg()` into `*pzErrMsg` on final failure.

Dynamic extension loading is gated by `SQLITE_LoadExtension`. `sqlite3_load_extension()` locks the connection mutex, calls the internal loader, and normalizes the result through `sqlite3ApiExit()`. The loader opens a shared object through the VFS, resolves the requested entry point or `sqlite3_extension_init`, calls it with `sqlite3Apis`, and records the library handle in `db->aExtension` so it can be closed with the connection. Auto-extensions use a process-global function-pointer array protected by `SQLITE_MUTEX_STATIC_MASTER`; `sqlite3AutoLoadExtensions()` snapshots each pointer under the mutex and invokes it outside that critical section.

`sqlite3Pragma()` is a long dispatch chain. Many read pragmas set VDBE result column names and emit rows immediately. Mutating pragmas either adjust connection fields (`db->flags`, `db->temp_store`, `db->dfltLockMode`, `db->nextPagesize`, `db->nextAutovac`, `sqlite3_temp_directory`) or emit opcodes such as `OP_SetCookie`, `OP_Pagecount`, `OP_MaxPgcnt`, `OP_JournalMode`, `OP_Checkpoint`, `OP_IncrVacuum`, and `OP_IntegrityCk`. At the end, if pager pragmas are enabled and the connection is in autocommit, it reapplies the btree safety level to reflect `synchronous`, `fullfsync`, or `checkpoint_fullfsync` changes.

Schema initialization starts in `sqlite3Init()`, which sets `db->init.busy`, initializes all non-temp databases first, then temp last so temp objects can refer to attached database objects. `sqlite3InitOne()` creates an in-memory definition for `sqlite_master` or `sqlite_temp_master`, opens a read transaction when needed, reads btree metadata cookies, validates text encoding and file format, sets cache size and schema state, then executes `SELECT name, rootpage, sql FROM '<db>'.sqlite_master ORDER BY rowid` with `sqlite3InitCallback()`. The callback parses each CREATE statement with `db->init.busy` set, so parser actions populate schema objects without generating executable VDBE code.

Preparing SQL flows through `sqlite3LockAndPrepare()`, which validates the database handle, enters the connection mutex and all btree mutexes, and calls `sqlite3Prepare()`. `sqlite3Prepare()` checks for schema table locks, unlocks pending virtual-table lists, optionally copies non-NUL-terminated SQL into a temporary buffer, runs the parser, verifies schema cookies when requested, resets internal schema on `SQLITE_SCHEMA`, installs EXPLAIN column names when needed, saves SQL text for v2 statements, finalizes failed VDBEs, and transfers parser errors to the connection error state. `sqlite3LockAndPrepare()` retries once on `SQLITE_SCHEMA`.

`sqlite3Reprepare()` recompiles a saved-SQL VDBE after schema change, swaps the new VDBE program into the old statement, transfers bindings, resets step result state, and finalizes the temporary VDBE. UTF-16 prepare variants convert SQL to UTF-8 first, call the UTF-8 prepare path, then map the UTF-8 tail pointer back to a byte offset in the original UTF-16 string.

The SELECT helpers are early transformations and inner-loop emitters. `sqlite3SelectNew()` owns all SELECT subtree pointers and handles allocation failure by clearing substructures. `sqlite3JoinType()` recognizes keyword combinations and rejects unsupported RIGHT/FULL joins. `sqliteProcessJoin()` rewrites NATURAL, ON, and USING clauses into extra WHERE terms, marking outer-join-originated expressions with `EP_FromJoin` and `iRightJoinTable` so WHERE planning preserves LEFT JOIN semantics. `selectInnerLoop()` evaluates or loads result columns, applies DISTINCT and OFFSET, then dispatches rows to the selected destination: output rows, coroutines, temp tables, sets for `IN`, scalar memory cells, EXISTS flags, or compound SELECT union/except tables.

## State And Persistence Behavior

Foreign-key state is not stored separately on disk by this code. Schema-loaded `FKey` objects represent parsed metadata; runtime enforcement updates VDBE foreign-key counters with `OP_FkCounter` and checks them with `OP_FkIfZero`. Deferred constraint state therefore lives in the executing VDBE/connection transaction state, while FK action triggers are cached in memory on `FKey.apTrigger[]`.

Insert persistence occurs only through emitted VDBE operations. Ordinary table writes are `OP_Insert` into the table btree plus `OP_IdxInsert` into each index. Virtual tables route through `OP_VUpdate`. AUTOINCREMENT tables persist sequence state in the `sqlite_sequence` table: begin code reads the current maximum rowid, row insertion updates the in-memory maximum with `OP_MemMax`, and end code rewrites or creates the `sqlite_sequence` row before statement exit.

The transfer optimization persists raw source records directly into destination table and index btrees. Because it bypasses expression evaluation and normal record reconstruction, it is only valid when source and destination schemas, collations, constraints, and index layouts are compatible. The destination-empty runtime check protects rowid and unique-index correctness when raw copy would otherwise be unsafe.

Pragma persistence varies by pragma. `default_cache_size`, `schema_version`, `user_version`, and auto-vacuum mode write btree metadata cookies through `OP_SetCookie`. `page_size` stores the requested next page size on the connection and calls `sqlite3BtreeSetPageSize()`, but it only takes effect while the database image can still change page size. `secure_delete`, `cache_size`, `locking_mode`, `journal_mode`, `journal_size_limit`, `auto_vacuum`, `incremental_vacuum`, and `synchronous` call into btree or pager state; some are connection-local, some are pager-file state, and some persist in database headers. `temp_store` and `temp_store_directory` can close the temp btree and reset schemas.

Schema initialization persists nothing in normal operation. It reads btree metadata and `sqlite_master` rows, then builds in-memory `Table`, `Index`, `Trigger`, `View`, and schema hash structures. It sets `DB_SchemaLoaded` and possibly `DB_Empty`; if corruption is detected it records `SQLITE_CORRUPT` unless recovery mode allows partial schema loading. `schemaIsValid()` later reads schema cookies from btrees and compares them with `Schema.schema_cookie`.

Prepared statements own VDBE programs and, for v2 prepare APIs, a copy of the SQL text via `sqlite3VdbeSetSql()`. That saved SQL enables automatic reprepare. Parser-local objects such as `TriggerPrg` lists are freed before returning. Error state is stored on the connection through `sqlite3Error()`, with allocation failures promoted to `db->mallocFailed`.

Extension state has two layers. Per-connection dynamically loaded shared-library handles are stored in `db->aExtension` and closed by `sqlite3CloseExtensions()`. Process-global auto-extension initializers are stored in writable static data `sqlite3Autoext` or the WSD replacement and protected by the master mutex. Loaded extension code receives pointers through the `sqlite3Apis` table, not by directly linking all symbols.

SELECT helper state is compile-time and VDBE-local. `Select` trees own expression/source/order/limit subtrees until deleted. `SelectDest` describes where result rows go. Temporary sorters and DISTINCT tables are ephemeral btrees opened by code elsewhere and written by helpers here with `OP_IdxInsert`, `OP_Sort`, `OP_Insert`, and related opcodes. Result column names, declaration types, and origin metadata are copied into VDBE column-name slots so they survive schema resets before statement deletion.

## Dependencies And Integration Points

This chunk depends heavily on the VDBE builder API: `sqlite3GetVdbe()`, `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, `sqlite3VdbeSetNumCols()`, `sqlite3VdbeSetColName()`, `sqlite3VdbeUsesBtree()`, `sqlite3VdbeFinalize()`, `sqlite3VdbeSetSql()`, `sqlite3VdbeSwap()`, and `sqlite3VdbeRunOnlyOnce()`. Nearly every SQL feature here is expressed by composing opcodes rather than executing storage operations directly during parse.

The btree and pager layers are integrated through table opening, schema metadata, pragmas, and schema validation: `sqlite3BtreeBeginTrans()`, `sqlite3BtreeCommit()`, `sqlite3BtreeGetMeta()`, `sqlite3BtreeSetCacheSize()`, `sqlite3BtreeSetPageSize()`, `sqlite3BtreeSecureDelete()`, `sqlite3BtreeSetAutoVacuum()`, `sqlite3BtreeGetAutoVacuum()`, `sqlite3BtreePager()`, `sqlite3PagerLockingMode()`, `sqlite3PagerJournalSizeLimit()`, and WAL checkpoint/autocheckpoint APIs.

Parser and resolver integration includes `sqlite3RunParser()`, `sqlite3ResolveExprNames()`, `sqlite3Select()`, `sqlite3WhereBegin()`, `sqlite3WhereEnd()`, `sqlite3ExprCode*()`, `sqlite3GenerateIndexKey()`, `sqlite3ExprCompare()`, `sqlite3ExprAnd()`, `sqlite3PExpr()`, `sqlite3SrcList*()`, trigger code generation, name-context handling, authorization checks, and schema lookup helpers.

Constraint and trigger integration is broad. Insert code consults `sqlite3TriggersExist()`, `sqlite3CodeRowTrigger()`, `sqlite3FkRequired()`, `sqlite3FkCheck()`, `sqlite3FkActions()`, `sqlite3HaltConstraint()`, conflict actions such as `OE_Abort`, `OE_Rollback`, `OE_Ignore`, `OE_Replace`, and trigger masks such as `TRIGGER_BEFORE` and `TRIGGER_AFTER`.

Virtual-table integration appears in insert support, transfer-optimization exclusion, `readsTable()` detection of `OP_VOpen`, schema preparation via `sqlite3VtabUnlockList()`, and extension APIs for `sqlite3_create_module`, `sqlite3_create_module_v2`, and `sqlite3_declare_vtab`.

VFS and OS integration appears in extension loading (`sqlite3OsDlOpen`, `sqlite3OsDlSym`, `sqlite3OsDlError`, `sqlite3OsDlClose`), temp directory validation (`sqlite3OsAccess`), and platform-specific lock proxy pragmas (`sqlite3OsFileControl` with `SQLITE_GET_LOCKPROXYFILE` and `SQLITE_SET_LOCKPROXYFILE`).

Compile-time feature flags gate large parts of the behavior: `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_AUTOINCREMENT`, `SQLITE_OMIT_XFER_OPT`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_OMIT_PRAGMA`, `SQLITE_OMIT_PAGER_PRAGMAS`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_SCHEMA_PRAGMAS`, `SQLITE_OMIT_WAL`, `SQLITE_OMIT_UTF16`, `SQLITE_OMIT_EXPLAIN`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_DEBUG`, `SQLITE_TEST`, and codec-related flags.

## Risks And Edge Cases

Foreign-key code is highly sensitive to immediate versus deferred behavior. `RESTRICT` must raise immediately even for otherwise deferred constraints, `NO ACTION` must remain deferrable when configured that way, and `DROP TABLE` must run the implicit delete before schema mutation because statement rollback cannot undo schema edits. Authorization returning `SQLITE_IGNORE` for parent-key reads intentionally makes parent values behave as NULL, which can alter enforcement.

Synthetic FK action triggers are cached objects with unusual allocation behavior. `fkActionTrigger()` disables lookaside for long-lived trigger allocation, builds expression trees manually, and stores the result on the `FKey`. Any mismatch between generated WHERE/WHEN expressions and actual FK semantics can cause incorrect cascades or missed violations.

`sqlite3Insert()` has many mutually dependent modes: views with INSTEAD OF triggers, ordinary tables, virtual tables with hidden columns, BEFORE triggers with unknown rowids, INSERT from SELECT coroutines, temp-table materialization, autoincrement, foreign keys, and count-changes. A change in register allocation, `keyColumn` mapping, or temp-table column numbering can break only one of these paths while leaving simpler inserts unaffected.

Conflict resolution can execute deletes before replacement inserts. That path must coordinate with triggers, FK checks, index cursors, rowid uniqueness, and statement abort behavior. The generated code must also keep `mayAbort` accurate so higher layers know whether a statement transaction is required.

The transfer optimization is intentionally narrow because it bypasses many normal checks. The runtime fallback path returns false after emitting partial VDBE code when the destination-empty check fails, so callers must be prepared to continue ordinary insert generation after that emitted halt/jump sequence. Compatibility checks must include collations, sort order, NOT NULL strength, CHECK expressions, unique indexes, and integer primary-key layout.

`sqlite3_exec()` callback arrays contain pointers into the active statement for column names and text values. Callers must consume them before returning. If text conversion fails for a non-NULL value, the function sets `db->mallocFailed` and exits. Callback abort finalizes the VDBE immediately and reports `SQLITE_ABORT`.

Extension loading is security-sensitive. It is disabled by default and controlled by `sqlite3_enable_load_extension()`, but once enabled it loads arbitrary shared libraries through the active VFS. The internal loader closes handles on symbol lookup or init failure, but if handle-array allocation fails after successful extension initialization, the code returns `SQLITE_NOMEM` without adding the handle to `db->aExtension`; the extension may already have registered functions or state.

The extension API table is ABI-sensitive. The code comments require new entries to be appended only. Omitted APIs are represented as NULL pointers, so extension code must check both library version and function pointer availability.

Pragma dispatch has a broad blast radius. `writable_schema` also enables recovery mode, `omit_readlock` and `read_uncommitted` alter locking semantics, `foreign_keys` cannot be toggled inside transactions, and flag pragmas expire prepared statements because they affect generated code. Changing temp storage inside a transaction is rejected; changing synchronous inside a transaction is rejected; page size changes can fail through pager realloc and set `mallocFailed`.

Schema-version pragmas are explicitly dangerous when used to write `schema_version`: they subvert SQLite's schema-cookie invalidation mechanism and can lead to stale prepared statements using an incorrect schema. The code permits this by emitting `OP_SetCookie`, so external callers can create hard-to-debug corruption or crashes.

Schema initialization trusts parsed `sqlite_master` SQL only after several corruption checks. Blank SQL is valid for implicit indexes but requires an existing index object to receive the root page. Recovery mode deliberately marks a partially loaded schema as loaded after errors, allowing later statements to access whatever schema subset survived.

Preparing SQL must guard against uncommitted schema changes from other connections. `sqlite3Prepare()` checks `sqlite3BtreeSchemaLocked()` under all btree mutexes before parsing. Missing this would allow a statement to compile against a schema state whose cookie might not detect a rolled-back concurrent schema edit.

UTF-16 prepare tail mapping is subtle. It converts to UTF-8 for parsing, then counts UTF-8 characters to locate the equivalent UTF-16 byte offset. Invalid or unusual Unicode sequences could stress this path, and `nBytes` handling differs between NUL-terminated and bounded SQL text.

Outer join rewriting depends on `EP_FromJoin` and `iRightJoinTable`. Terms from `ON` and `USING` must be deferred correctly during WHERE planning so LEFT JOIN rows are preserved when the right side is NULL-extended. The code rejects RIGHT and FULL OUTER JOIN despite recognizing their keywords.

ORDER BY with LIMIT is implemented in sorter insertion by deleting the current last sorter entry once the limit is exceeded. This depends on sorter key order, the sequence column, and OFFSET accounting. SELECT destinations also have special cases: `SRT_Exists` ignores actual result expressions, scalar subquery destinations require one column, and `SRT_Set` preserves ORDER BY only because LIMIT may make order observable.

Result metadata generation recurses through views and subqueries to determine declaration type and origin names. It returns NULL for non-column expressions and for some correlated subquery column references that cannot be mapped in the current `NameContext`. Consumers must tolerate absent metadata.

## Test Signals

Foreign-key tests should cover child insert/delete/update, parent update/delete, immediate versus deferred counters, `RESTRICT` versus `NO ACTION`, cascade/set-null/set-default actions, authorization returning `SQLITE_IGNORE`, trigger-disabled `DROP TABLE` cleanup, and cleanup of cached action triggers.

Insert tests should cover VALUES and SELECT sources, explicit and implicit rowid insertion, NULL rowid replacement with generated rowid, BEFORE and AFTER triggers, INSTEAD OF view triggers, virtual tables and hidden columns, default values, count-changes, self-referential `INSERT ... SELECT` materialization, autoincrement sequence read/write, and rollback after constraint failures.

Constraint tests should exercise NOT NULL, CHECK, rowid uniqueness, multiple UNIQUE indexes, each conflict policy (`ROLLBACK`, `ABORT`, `FAIL`, `IGNORE`, `REPLACE`), replacement deletes interacting with triggers and foreign keys, and memory-failure paths while constructing index affinity strings or constraint records.

Transfer-optimization tests should include the exact fast path and near misses: destination triggers, views, virtual tables, mismatched column counts, mismatched collations, mismatched index sort order, different CHECK constraints, destination not empty with unique indexes, integer-primary-key collisions, and AUTOINCREMENT destination updates.

`sqlite3_exec()` tests should cover multiple statements in one string, comments/whitespace-only inputs, callback abort, NULL callback with and without `SQLITE_NullCallback`, schema-change retry, text conversion failures, and returned error-message ownership.

Extension-loading tests should verify disabled-by-default behavior, enabling/disabling per connection, missing library, missing entry point, extension init failure with error text, handle cleanup on close, omitted API table entries under compile flags, duplicate auto-extension registration, reset of auto-extensions, and auto-extension failure propagation to the connection error state.

Pragma tests should cover query and setter forms for cache/page size, secure delete, page count, max page count, locking mode, journal mode, journal size limit, auto-vacuum, incremental vacuum, temp store, temp directory, synchronous, flag pragmas, table/index/database/collation/foreign-key list outputs, integrity and quick check, encoding, schema/user/free-list cookies, compile options, WAL checkpoint/autocheckpoint, and debug/codec-only pragmas when compiled in.

Schema and prepare tests should cover empty databases, temp schema loaded last, attached databases with mismatched encodings, unsupported file formats, malformed `sqlite_master` rows, implicit indexes with blank SQL, recovery-mode partial schema loading, schema-cookie mismatch causing `SQLITE_SCHEMA`, locked schema tables causing `SQLITE_LOCKED`, v2 automatic reprepare with binding transfer, legacy prepare returning schema errors, bounded SQL strings without trailing NUL, SQL length limit, EXPLAIN and EXPLAIN QUERY PLAN column names, and UTF-16 prepare tail pointers.

SELECT helper tests should cover NATURAL joins, ON and USING rewriting, illegal NATURAL with ON/USING, illegal ON plus USING, unsupported RIGHT/FULL joins, LEFT JOIN predicate preservation, DISTINCT with and without ORDER BY, ORDER BY plus LIMIT/OFFSET sorter behavior, compound SELECT destinations, scalar subquery multi-column errors, EXISTS destination skipping expression evaluation, result column names under `short_column_names`/`full_column_names`, declaration types through views/subqueries, and column-origin metadata when enabled.

FoundationDB-specific reconciliation should note that this amalgamation slice is mostly upstream SQLite SQL-layer code. Its runtime behavior still depends on the FoundationDB-vendored btree/pager modifications documented in neighboring chunks, especially around page-size handling, lazy/range deletion, pointer-map behavior, and pager/WAL semantics invoked by pragmas and generated VDBE programs.

### subset-b-008416: lines 75678-83001

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 75678-83001

## Scope

This chunk covers the tail of SQLite `select.c`, then full or partial sections of `table.c`, `trigger.c`, `update.c`, `vacuum.c`, `vtab.c`, and the opening of `where.c` in the FoundationDB-vendored SQLite 3.7.6 amalgamation. The code is almost entirely parser/code-generator and schema/virtual-table infrastructure: it converts resolved parse trees into VDBE programs, manages trigger and virtual-table metadata, implements UPDATE and VACUUM code paths, and starts WHERE-clause optimizer analysis.

The covered line range is not a self-contained feature boundary. It begins inside result-column derivation for SELECT statements and ends inside the comments for OR-clause analysis in the WHERE optimizer.

## Purpose

The main purpose of this chunk is to bridge high-level SQL constructs to lower-level VDBE and B-tree behavior:

- SELECT result metadata, compound SELECT execution, query flattening, aggregate execution, DISTINCT, ORDER BY, GROUP BY, LIMIT, and simple count/min/max optimizations.
- The legacy `sqlite3_get_table()` wrapper that materializes callback results into a heap-allocated table.
- CREATE/DROP trigger parsing, trigger-step representation, trigger subprogram compilation, trigger invocation, and old/new column mask discovery.
- UPDATE statement code generation for ordinary tables, views with INSTEAD OF triggers, foreign keys, rowid changes, index maintenance, one-pass updates, and virtual table updates.
- VACUUM implementation by copying the main database into an attached temporary database and then copying the compacted B-tree file back.
- Virtual table module registration, CREATE VIRTUAL TABLE parsing, schema declaration, xCreate/xConnect/xDestroy, vtab transaction hooks, function overloading, and write-lock tracking.
- Initial WHERE optimizer structures and helper routines that decompose predicates into indexable terms.

For the FoundationDB integration, the persistence-sensitive code in this chunk is especially relevant around UPDATE, VACUUM, virtual table callbacks, schema cookies, temporary B-trees, and VDBE opcodes that open/write/delete records.

## SELECT Code Generation

The opening functions build SELECT result metadata:

- `selectColumnsFromExprList()` derives a `Column[]` list from a SELECT expression list. It chooses names from explicit `AS` aliases, source-table column names, identifiers, or expression spans, then appends `:N` suffixes to make names unique.
- `selectAddColumnTypeAndCollation()` fills in result column type strings, affinity, and collation by inspecting resolved expressions.
- `sqlite3ResultSetOfSelect()` prepares a SELECT, forces short column names while deriving metadata, allocates a transient `Table`, and populates `Table.aCol`, `Table.nCol`, `Table.nRowEst`, and `Table.iPKey`.
- `sqlite3GetVdbe()` lazily allocates the statement VDBE and adds `OP_Trace` when tracing is enabled.
- `computeLimitRegisters()` emits VDBE code to evaluate `LIMIT` and `OFFSET`, stores counters in `Select.iLimit` and `Select.iOffset`, clamps row estimates for integer limits, and jumps to the query end for `LIMIT 0`.

Compound SELECTs are handled by `multiSelect()` and `multiSelectOrderBy()`:

- `multiSelect()` validates that only the rightmost SELECT has `ORDER BY` or `LIMIT`, checks result-column count compatibility, and handles `UNION ALL`, `UNION`, `EXCEPT`, and `INTERSECT`.
- `UNION ALL` reuses the same LIMIT/OFFSET registers across the left and right SELECTs, allowing the right side to be skipped once the limit is reached.
- `UNION` and `EXCEPT` use an ephemeral table keyed by result rows. The left query inserts rows, the right query either inserts more (`UNION`) or removes matching rows (`EXCEPT`), and a final scan converts the temporary table into the requested destination.
- `INTERSECT` uses two ephemeral tables, scans the first, checks each record against the second with `OP_NotFound`, and emits only common rows.
- `multiSelectOrderBy()` implements ordered compound queries with two coroutines, one for the left input and one for the right input. It creates comparison `KeyInfo`, ORDER BY permutations, duplicate-removal state, output subroutines, EOF handlers, and a merge loop driven by `OP_Compare` and `OP_Jump`.

Subquery flattening is implemented by `substExpr()`, `substExprList()`, `substSelect()`, and `flattenSubquery()`. `flattenSubquery()` enforces SQLite's long list of safety restrictions, including aggregate/DISTINCT/LIMIT/ORDER BY interactions, left-join restrictions, compound-subquery restrictions, and OFFSET exclusion. When permitted, it rewrites the outer query's FROM list and expressions so references to the subquery result cursor are replaced with copies of the subquery result expressions. For compound `UNION ALL` subqueries, it duplicates the parent SELECT into a matching compound chain.

`sqlite3Select()` is the central SELECT code generator in this chunk. Its major control flow is:

1. Authorize SELECT and call `sqlite3SelectPrep()`.
2. Expand/materialize FROM subqueries, attempting `flattenSubquery()` before falling back to `SRT_EphemTab`.
3. Route compound SELECTs through `multiSelect()`.
4. Rewrite simple `DISTINCT` to `GROUP BY` when possible, because GROUP BY may use indexes.
5. Open ORDER BY and DISTINCT ephemeral structures when needed.
6. For non-aggregate queries, call `sqlite3WhereBegin()`, run `selectInnerLoop()`, then `sqlite3WhereEnd()`.
7. For aggregate queries, analyze aggregate expressions into `AggInfo`, then choose GROUP BY or single-group logic.
8. Generate sort tail and output metadata as needed.

Aggregate helpers include:

- `resetAccumulator()` initializes aggregate memory registers and opens per-aggregate DISTINCT ephemeral tables.
- `updateAccumulator()` evaluates aggregate arguments, handles DISTINCT filtering, emits `OP_CollSeq` for collation-sensitive aggregates, and emits `OP_AggStep`.
- `finalizeAggFunctions()` emits `OP_AggFinal`.
- `isSimpleCount()` recognizes `SELECT count(*) FROM table` with no WHERE/GROUP BY/subquery/view/virtual table and enables `OP_Count`.
- `minMaxQuery()` recognizes single `min(column)` or `max(column)` aggregate forms so the WHERE planner can try an ordered scan and break after the first useful row.

Important VDBE opcodes emitted here include `OP_OpenEphemeral`, `OP_Rewind`, `OP_Next`, `OP_Sort`, `OP_Compare`, `OP_Permutation`, `OP_Yield`, `OP_Gosub`, `OP_Return`, `OP_If`, `OP_IfZero`, `OP_IfPos`, `OP_AggStep`, `OP_AggFinal`, `OP_Count`, `OP_ResultRow`, and `OP_Close`.

## Table API Wrapper

`table.c` implements the optional `sqlite3_get_table()` and `sqlite3_free_table()` APIs:

- `TabResult` accumulates all callback output from `sqlite3_exec()`.
- `sqlite3_get_table_cb()` allocates/expands a `char **` result array, stores column names as the first row, copies row values, rejects incompatible column counts across multiple statements, and maps allocation failure to `SQLITE_NOMEM`.
- `sqlite3_get_table()` initializes `TabResult`, runs `sqlite3_exec()`, stores the element count in the hidden slot immediately before the returned pointer, shrinks the result array when possible, and returns row/column counts.
- `sqlite3_free_table()` walks the hidden element count and frees every non-null string and the containing array.

This is a convenience API layered on normal statement execution. It persists no database state, but it is sensitive to memory ownership conventions because callers free the shifted pointer returned by `sqlite3_get_table()`.

## Trigger Infrastructure

The trigger section manages both persistent trigger schema entries and per-statement executable subprograms.

Schema and parsing functions:

- `sqlite3TriggerList()` combines table-local triggers with TEMP triggers that target the same table.
- `sqlite3BeginTrigger()` validates trigger name/database placement, target table existence, virtual-table exclusion, system-table exclusion, view/table timing rules, authorization, and duplicate names. It builds `Parse.pNewTrigger`.
- `sqlite3FinishTrigger()` attaches parsed steps, fixes database qualifications, writes the `sqlite_master` entry for new triggers, reparses schema, or inserts the trigger into the schema hash during initialization.
- `sqlite3TriggerSelectStep()`, `sqlite3TriggerInsertStep()`, `sqlite3TriggerUpdateStep()`, and `sqlite3TriggerDeleteStep()` build reduced copies of trigger body statements.
- `sqlite3DeleteTriggerStep()` and `sqlite3DeleteTrigger()` free trigger trees and trigger-step lists.
- `sqlite3DropTrigger()` resolves a trigger name, preferring TEMP before MAIN for unqualified names.
- `sqlite3DropTriggerPtr()` emits VDBE code that deletes the matching `sqlite_master` row, changes the schema cookie, and emits `OP_DropTrigger`.
- `sqlite3UnlinkAndDeleteTrigger()` removes an in-memory trigger from the schema hash and table trigger list.

Execution functions:

- `sqlite3TriggersExist()` returns the trigger list only if at least one trigger matches operation, timing, and UPDATE column overlap.
- `targetSrcList()` builds a trigger-step target `SrcList`, qualifying it with the trigger database unless the trigger is TEMP.
- `codeTriggerProgram()` walks trigger steps and emits nested INSERT/UPDATE/DELETE/SELECT code. Statement-level ON CONFLICT overrides trigger-step conflict policy.
- `codeRowTrigger()` compiles a trigger into a `SubProgram`, resolving the WHEN clause, emitting an early halt if it is false/null, compiling body statements, and recording old/new column masks.
- `getRowTrigger()` caches compiled trigger programs by trigger pointer and conflict policy in the top-level `Parse`.
- `sqlite3CodeRowTriggerDirect()` emits parent `OP_Program` with the trigger subprogram and sets P5 to block recursive trigger invocation when recursive triggers are disabled.
- `sqlite3CodeRowTrigger()` filters a trigger list by operation, timing, and UPDATE column overlap, then emits each matching trigger.
- `sqlite3TriggerColmask()` compiles or reuses trigger programs to discover which `old.*` or `new.*` columns are read, allowing UPDATE/DELETE code to avoid loading unused columns.

State is split between durable schema rows in `sqlite_master`, in-memory `Schema.trigHash` and `Table.pTrigger`, parse-time `TriggerStep` trees, and VDBE `SubProgram` objects linked from the parent statement.

## UPDATE Code Generation

`sqlite3ColumnDefault()` annotates the most recent `OP_Column` with a P4 default value for columns added by ALTER TABLE and emits `OP_RealAffinity` when a REAL-affinity column may be read from integer storage.

`sqlite3Update()` is the main UPDATE compiler. Its key stages are:

1. Resolve the target table, trigger mask, view status, read-only status, and UPDATE column mapping `aXRef`.
2. Resolve SET expressions and detect rowid changes via INTEGER PRIMARY KEY or rowid aliases.
3. Ask foreign-key code whether old/new FK checks are required.
4. Allocate table/index cursors and per-index registers only for indexes affected by changed columns, unless rowid changes or REPLACE conflict handling require broader access.
5. For virtual tables, delegate to `updateVirtualTable()`.
6. Allocate old rowid, new rowid, old column, and new column registers.
7. Materialize views when updating a view with INSTEAD OF triggers.
8. Use `sqlite3WhereBegin()` to find candidate rows. If one-pass update is not possible, store candidate rowids in a `RowSet`.
9. Open the table and needed indexes for write.
10. Loop candidate rows, recompute rowid when needed, load old columns required by triggers/FKs, compute new column values, fire BEFORE triggers, reload unchanged columns after BEFORE triggers, check constraints and foreign keys, delete old index entries, delete or update the table row, insert new indexes/record, run FK actions, increment row count, and fire AFTER triggers.
11. Close cursors, finish autoincrement bookkeeping, optionally return `"rows updated"`, and free parse-owned inputs.

The one-pass path uses a WHERE plan that can update as it scans without first materializing rowids. The fallback path avoids scan invalidation by collecting rowids first. BEFORE trigger behavior is explicitly documented as undefined if the trigger deletes or renames the row being updated; the generated code checks `OP_NotExists` and skips further work for deleted rows.

`updateVirtualTable()` builds a synthetic SELECT that returns the original rowid, optional new rowid, and all post-update column values. It stores these rows in an ephemeral table, then scans it and emits `OP_VUpdate` for each row. It calls `sqlite3VtabMakeWritable()` so an `OP_VBegin` will be generated for the virtual table transaction.

Persistence-facing UPDATE behavior includes schema write checks, table locks, index B-tree updates, rowid mutation, constraint enforcement, FK checks/actions, autoincrement finalization, and trigger subprogram execution.

## VACUUM

`sqlite3Vacuum()` emits `OP_Vacuum`; `sqlite3RunVacuum()` implements that opcode.

`sqlite3RunVacuum()` requires autocommit mode and no other active SQL statements. It saves connection flags, change counters, and tracing, then temporarily enables writable schema, ignores CHECK constraints, prefers built-ins, disables foreign keys, disables reverse-order scans, and suppresses tracing.

The algorithm is:

1. Attach a temporary database as `vacuum_db`, either in memory or as a temp file.
2. Unlock the temporary B-tree left locked by schema reading.
3. Copy page-size/reserve settings from main, except that encrypted and WAL databases cannot change page size through VACUUM.
4. Set temp synchronous to OFF and mirror auto-vacuum mode.
5. Begin an exclusive transaction.
6. Recreate tables and indexes in `vacuum_db` from `main.sqlite_master`.
7. Copy table contents with generated `INSERT INTO vacuum_db.X SELECT * FROM main.X`.
8. Copy `sqlite_sequence` content when present.
9. Copy view, trigger, and virtual-table `sqlite_master` rows directly.
10. Preserve selected B-tree meta values, incrementing the schema cookie.
11. Copy the compacted temporary B-tree file back into the main B-tree with `sqlite3BtreeCopyFile()`.
12. Commit the temp B-tree, copy auto-vacuum mode/page size back, restore flags/counters/tracing, detach the temp database manually, and reset internal schema.

Risks are concentrated around transaction boundaries and file format metadata. VACUUM directly manipulates B-tree page size, reserve bytes, schema cookies, auto-vacuum state, and the entire main database file image. In this FoundationDB vendored copy, any custom pager/VFS behavior must preserve the assumptions behind attach, temp database creation, B-tree copy, journal cleanup, and schema reset.

## Virtual Tables

The virtual table section implements registration, schema construction, lifecycle, transactions, and function overloading.

Module registration:

- `createModule()` installs a `Module` into `db->aModule`, replacing an existing module and calling its destructor when appropriate.
- `sqlite3_create_module()` and `sqlite3_create_module_v2()` are public API wrappers.

Connection-specific virtual table objects:

- `sqlite3GetVTable()` finds the `VTable` object for a given `sqlite3*` connection.
- `sqlite3VtabLock()`/`sqlite3VtabUnlock()` manage nested reference counts and call module `xDisconnect()` when the count reaches zero.
- `vtabDisconnectAll()` moves per-connection `VTable` objects from `Table.pVTable` to each connection's deferred disconnect list, except optionally preserving the current connection's entry.
- `sqlite3VtabUnlockList()` drains `db->pDisconnect` while holding all required B-tree/database mutexes and expires prepared statements.
- `sqlite3VtabClear()` clears virtual-table module arguments and schedules/disconnects VTable objects before deleting the `Table`.

CREATE VIRTUAL TABLE parsing:

- `sqlite3VtabBeginParse()` starts a virtual table definition, marks the table `TF_Virtual`, and seeds module arguments with module name, database name, and table name.
- `sqlite3VtabArgInit()`/`sqlite3VtabArgExtend()` collect raw module argument token ranges.
- `sqlite3VtabFinishParse()` stores the complete CREATE VIRTUAL TABLE SQL in `sqlite_master`, emits `OP_VCreate`, expires statements, and reparses schema for real creation. During schema load, it installs the in-memory table without calling `xConnect()`.
- `addModuleArgument()` owns argument strings through `Table.azModuleArg`.

Constructors and schema declaration:

- `vtabCallConstructor()` allocates a `VTable`, sets `db->pVTab`, invokes `xCreate` or `xConnect`, requires the module to call `sqlite3_declare_vtab()`, links the VTable into `Table.pVTable`, and processes `"hidden"` column type tokens.
- `sqlite3VtabCallConnect()` lazily connects a loaded virtual table the first time it is used.
- `sqlite3VtabCallCreate()` invokes module `xCreate` for a newly created virtual table and adds it to the virtual table transaction list.
- `sqlite3_declare_vtab()` parses a CREATE TABLE statement supplied by the module and transfers its column definitions to the pending virtual table.
- `sqlite3VtabCallDestroy()` invokes `xDestroy()` on DROP TABLE and removes the VTable from `Table.pVTable`.

Virtual-table transaction hooks:

- `addToVTrans()` grows `db->aVTrans` and locks each participating VTable.
- `sqlite3VtabBegin()` calls `xBegin()` once per virtual table per transaction, unless called while virtual tables are syncing, in which case it returns `SQLITE_LOCKED`.
- `sqlite3VtabSync()` calls `xSync()` on each transaction participant and preserves the first error and message.
- `sqlite3VtabCommit()` and `sqlite3VtabRollback()` use `callFinaliser()` to call `xCommit()` or `xRollback()` and clear `db->aVTrans`.
- `sqlite3VtabMakeWritable()` records tables needing an eventual `OP_VBegin`.

`sqlite3VtabOverloadFunction()` lets a virtual table override functions such as MATCH/LIKE/GLOB/REGEXP for expressions whose first argument is a column of that virtual table. It calls module `xFindFunction()` and creates an ephemeral `FuncDef` when overloaded.

## WHERE Optimizer Opening

The start of `where.c` defines predicate-analysis structures and helpers used later by `sqlite3WhereBegin()`.

Important types:

- `WhereTerm` records one WHERE subexpression, its operator mask, left cursor/column, prerequisite table masks, parent/child relationships for virtual terms, and optional OR/AND analysis payloads.
- `WhereClause` owns an array of `WhereTerm` values and a `WhereMaskSet`.
- `WhereOrInfo` holds decomposed OR terms and the set of tables for which the OR is indexable.
- `WhereAndInfo` holds decomposed AND terms inside a larger OR term.
- `WhereMaskSet` maps sparse VDBE cursor numbers to dense `Bitmask` bits.
- `WhereCost` stores a candidate `WherePlan`, total cost, and used table mask.

Operator and plan flags:

- `WO_*` masks represent exploitable term operators: `IN`, equality, inequalities, `MATCH`, `IS NULL`, compound OR/AND, and no-op terms.
- `WHERE_*` flags represent chosen strategies: rowid equality/range, column equality/range/IN/NULL, index-only scans, ORDER BY satisfaction, reverse scans, uniqueness, virtual table processing, multi-index OR, and temporary indexes.

Helper routines:

- `whereClauseInit()`, `whereClauseClear()`, `whereClauseInsert()`, `whereOrInfoDelete()`, and `whereAndInfoDelete()` manage `WhereClause` storage and ownership of dynamic/virtual expressions.
- `whereSplit()` recursively decomposes a predicate by `TK_AND` or `TK_OR`.
- `initMaskSet`, `getMask()`, and `createMask()` maintain cursor-to-bit mappings.
- `exprTableUsage()`, `exprListTableUsage()`, and `exprSelectTableUsage()` compute table dependency masks after name resolution.
- `allowedOp()` and `operatorMask()` decide which expression operators are indexable and map token operators to `WO_*`.
- `exprCommute()` rewrites `X op Y` into `Y op X` while preserving comparison collation semantics and flipping inequality direction.
- `findTerm()` searches analyzed terms for constraints usable by a given cursor/column/operator set and, when an index is provided, checks affinity and collation compatibility.
- `exprAnalyzeAll()` applies the later `exprAnalyze()` routine to every term.
- `isLikeOrGlob()` recognizes LIKE/GLOB calls that can be transformed into prefix range constraints. It requires a TEXT-affinity column on the left and a literal or bound string pattern on the right that does not begin with a wildcard.
- `isMatchOfColumn()` recognizes virtual-table `column MATCH expr` forms.
- `transferJoinMarkings()` carries outer-join origin metadata to derived optimizer expressions.

The chunk ends as the comments introduce OR-clause analysis. The described optimization creates either an equivalent virtual `IN` term for same-column OR equality chains or marks indexable OR subterms for multi-index OR planning.

## State and Persistence Behavior

Key mutable state in this chunk includes:

- `Parse` counters for VDBE memory registers, cursor numbers, labels, nested parse contexts, and trigger programs.
- `Select` fields such as `pPrior`, `pOrderBy`, `pLimit`, `pOffset`, `iLimit`, `iOffset`, `nSelectRow`, `selFlags`, and ephemeral cursor addresses.
- `AggInfo` arrays and accumulator registers for aggregate queries.
- Schema structures for triggers and virtual tables: `Schema.trigHash`, `Table.pTrigger`, `Table.pVTable`, `Table.azModuleArg`, `sqlite3.aModule`, `sqlite3.aVTrans`, and `sqlite3.pDisconnect`.
- VDBE ephemeral B-trees for compound SELECTs, GROUP BY, DISTINCT, ORDER BY, virtual-table UPDATE staging, and trigger/drop schema scans.
- Persistent tables and indexes modified by UPDATE via `OP_OpenWrite`, index-delete helpers, table deletes, completed insertions, FK checks/actions, and autoincrement finalization.
- `sqlite_master` rows and schema cookies modified by trigger creation/drop, CREATE VIRTUAL TABLE, and VACUUM.
- Whole-file B-tree page layout and metadata modified by VACUUM.

Most code here does not directly call the pager. It emits VDBE operations or uses B-tree APIs, so persistence effects occur later during VDBE execution or through B-tree helper calls in VACUUM.

## Dependencies and Integration Points

This chunk depends heavily on earlier declarations and helper subsystems:

- Expression analysis/codegen: `sqlite3ResolveExprNames()`, `sqlite3ExprCode*()`, `sqlite3ExprAnalyzeAggList()`, `sqlite3ExprCollSeq()`, `sqlite3ExprAffinity()`, expression/list duplication and deletion.
- VDBE construction: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, labels, comments, `OP_*` opcodes, `KeyInfo`, and subprograms.
- WHERE planner: `sqlite3WhereBegin()` and `sqlite3WhereEnd()` are called by SELECT and UPDATE; their internal term-analysis structures begin at the end of this chunk.
- Schema and authorization: schema hash tables, `sqlite3ReadSchema()`, `sqlite3FindTable()`, `sqlite3SrcListLookup()`, `sqlite3Fix*()` routines, `sqlite3AuthCheck()`, schema cookies, and `OP_ParseSchema`.
- DML helpers: insert/delete/update support, row/index delete generation, constraint checks, complete insertion, autoincrement, FK checks/actions.
- Virtual table public API: `sqlite3_module`, `sqlite3_vtab`, `sqlite3_index_info`, `xCreate`, `xConnect`, `xDisconnect`, `xDestroy`, `xBegin`, `xSync`, `xCommit`, `xRollback`, and `xFindFunction`.
- B-tree/pager layer: VACUUM uses `sqlite3Btree*()` and pager journal-mode/page-size APIs directly.

## Risks and Edge Cases

- Subquery flattening is intentionally conservative. Incorrectly relaxing restrictions can change LEFT JOIN null-extension semantics, LIMIT/OFFSET behavior, DISTINCT/aggregate ordering, or compound SELECT results.
- Compound SELECT code mutates `Select` links and LIMIT/OFFSET pointers temporarily. Error paths must restore ownership enough for `sqlite3SelectDelete()` to free the tree correctly.
- Aggregate code relies on clearing expression caches before accumulator writes. The comment references ticket `[883034dcb5]`, where shallow copies of cached text/blob values could be invalidated.
- Trigger compilation caches `SubProgram` objects by trigger pointer and conflict policy. Recursive trigger behavior depends on `SQLITE_RecTriggers` and OP_Program P5.
- UPDATE with BEFORE triggers deliberately has undefined behavior when the trigger deletes or renames the row being updated. The generated code detects deletion and skips the remaining work.
- UPDATE authorization handling can set `aXRef[j] = -1` for ignored columns; code paths must not later assume every SET target remains active.
- `sqlite3Update()` allocates `aRegIdx` with `sizeof(Index*) * nIdx` even though the variable type is `int *`. On platforms where pointer size exceeds int size this overallocates, but it is a noteworthy local oddity.
- VACUUM is not allowed inside a transaction or with other active statements. It temporarily disables foreign keys and checks, manipulates schema directly, and copies the full B-tree file image; any custom storage backend must match SQLite's assumptions around attach/temp DBs, B-tree copy, and journal cleanup.
- Virtual table constructors must call `sqlite3_declare_vtab()`. If they return success without declaring schema, SQLite reports an error.
- Virtual table transaction writes during `xSync()` are blocked with `SQLITE_LOCKED`.
- `sqlite3VtabUnlockList()` relies on specific mutex ownership. In this FoundationDB build, earlier chunk settings indicate SQLite mutexes may be omitted, so the embedding layer must preserve equivalent serialization.
- LIKE/GLOB optimization depends on bound parameter values at prepare/reprepare time and marks variables with `sqlite3VdbeSetVarmask()` so changes force replanning.
- WHERE term arrays can reallocate in `whereClauseInsert()`, invalidating saved `WhereTerm *` pointers.

## Test Signals

Useful test coverage for this chunk should include:

- SELECT column-name derivation with duplicate aliases, source columns, rowid expressions, expressions without aliases, and collations/types from views/subqueries.
- Compound SELECT variants: `UNION ALL`, `UNION`, `EXCEPT`, `INTERSECT`, with and without `ORDER BY`, `LIMIT`, `OFFSET`, duplicate rows, and collation-sensitive ordering.
- Subquery flattening cases that should flatten and cases blocked by DISTINCT, aggregate, LEFT JOIN right operand, LIMIT/OFFSET, parent WHERE, parent DISTINCT, and compound-subquery restrictions.
- Aggregate paths: GROUP BY with and without sort, DISTINCT aggregate argument count errors, `count(*)` fast path, `min()`/`max()` by index, HAVING filtering, and ORDER BY tail generation.
- `sqlite3_get_table()` with empty results, multiple statements with incompatible column counts, NULL values, allocation failures, and free-table ownership.
- Trigger creation/drop for TEMP vs main schemas, triggers on views vs tables, prohibited virtual/system tables, WHEN clauses, UPDATE OF column filtering, recursive trigger settings, and schema reparse effects.
- UPDATE scenarios covering rowid changes, indexed and non-indexed columns, REPLACE conflicts, one-pass and RowSet plans, BEFORE/AFTER triggers, FK checks/actions, views with INSTEAD OF triggers, count-rows output, and virtual table UPDATE.
- VACUUM with normal file DBs, in-memory temp vacuum DBs, WAL mode page-size preservation, `sqlite_sequence`, triggers/views/virtual tables in schema, active statement rejection, transaction rejection, and schema-cookie changes.
- Virtual table module replacement/destructors, lazy xConnect, xCreate/xDestroy, schema declaration failures, hidden columns, vtab transaction begin/sync/commit/rollback, xFindFunction overloading, and writes attempted during xSync.
- WHERE-analysis unit coverage through query plans for equality, range, IN, IS NULL, LIKE/GLOB prefix optimization, MATCH on virtual tables, OR-to-IN transformation, multi-index OR, collation mismatches, and affinity mismatches.

### subset-b-008417: lines 83002-89544

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 83002-89544

## Scope And Purpose

This chunk covers the tail of SQLite's `where.c` query-planner and WHERE-loop code generator, followed by the beginning of the generated Lemon parser implementation in `parse.c`. In this vendored amalgamation, the first part analyzes WHERE terms, chooses table/index access plans, emits VDBE loops for rowid, index, virtual-table, OR, and full-table scans, and closes/freezes the `WhereInfo` state. The second part defines parser helper structures, parser action tables, parser stack mechanics, destructors, token/rule tracing metadata, and the first grammar reduction actions for transaction, schema, constraint, and SELECT syntax.

The WHERE planner/codegen section is responsible for turning parsed SQL predicates into executable VDBE cursor loops. It recognizes OR-to-IN transformations, BETWEEN/LIKE/MATCH/STAT2 virtual terms, ORDER BY satisfied by indexes, automatic transient covering indexes, virtual-table `xBestIndex` plans, range selectivity estimates, join ordering, LEFT JOIN null-row handling, EXPLAIN QUERY PLAN output, and cleanup of cursors and temporary planner state.

The parser section is generated infrastructure. It does not choose query plans itself, but it is the entry point that builds parse-tree objects and invokes semantic actions such as `sqlite3BeginTransaction()`, `sqlite3StartTable()`, `sqlite3AddColumn()`, `sqlite3CreateIndex()`, `sqlite3SelectNew()`, and `sqlite3Select()`. The chunk ends mid-`yy_reduce()` after the `orderby_opt` empty-rule case begins, so many later grammar reductions are outside this work item.

## Important APIs, Types, And Functions

`exprAnalyzeOrTerm()` breaks an OR expression into subterms, analyzes each subterm, and classifies the OR as either optimizable through a virtual `IN` term or through multi-index OR rowid union. It allocates `WhereOrInfo`, stores a nested `WhereClause`, computes `WhereOrInfo.indexable`, and may insert a virtual `TK_IN` term with `TERM_VIRTUAL|TERM_DYNAMIC`.

`exprAnalyze()` is the main WHERE-term analyzer for one `WhereTerm`. It fills prerequisite bitmasks, `leftCursor`, `u.leftColumn`, and `eOperator`; commutes column comparisons by adding virtual terms; expands BETWEEN into `>=` and `<=`; dispatches OR analysis; creates LIKE/GLOB range terms; creates MATCH terms for virtual tables; and, under `SQLITE_ENABLE_STAT2`, creates a `x>NULL` virtual term for `x IS NOT NULL`.

`referencesOtherTables()` and `isSortingIndex()` determine whether an index scan can satisfy an ORDER BY clause. `isSortingIndex()` matches ORDER BY column/collation/sort-order terms against index columns, allows equality-constrained index prefixes to be skipped, treats rowid uniqueness specially, and sets the reverse-scan flag through `pbRev`.

`bestOrClauseIndex()` estimates and records a `WHERE_MULTI_OR` plan by recursively pricing each OR subterm with `bestIndex()`, summing costs/row counts, adding sort cost if needed, and storing the chosen OR `WhereTerm` in `WhereCost.plan.u.pTerm`.

`termCanDriveIndex()`, `bestAutomaticIndex()`, and `constructAutomaticIndex()` implement automatic transient indexes. The planner only considers equality terms with compatible affinity, estimates whether building the temporary covering index beats a full scan, and later emits VDBE code to open `OP_OpenAutoindex`, fill it with `sqlite3GenerateIndexKey()`, and insert entries with `OP_IdxInsert`.

Virtual-table integration is handled by `allocateIndexInfo()`, `vtabBestIndex()`, and `bestVirtualIndex()`. They build/reuse `sqlite3_index_info`, map `WhereTerm` constraints into `aConstraint[]`, expose ORDER BY columns when all terms are on the virtual table, recompute constraint `usable` flags per join order, call module `xBestIndex`, validate `argvIndex` use, and transfer estimated cost/order consumption into `WhereCost`.

Range and histogram estimation uses `whereRangeRegion()`, `valueFromExpr()`, `whereRangeScanEst()`, `whereEqualScanEst()`, and `whereInScanEst()` when `SQLITE_ENABLE_STAT2` is enabled. These functions derive literal or bound-parameter values, compare them against `Index.aSample[]`, account for collation/encoding, and refine selectivity for range, equality, and `IN (...)` constraints. Without STAT2, range selectivity falls back to quartering the candidate row set per bound.

`bestBtreeIndex()` is the main b-tree access planner. It walks the rowid pseudo-index and real indexes, counts usable equality and IN constraints, finds one range-constrained column, estimates row count and cost, accounts for IN loop multipliers, covering-index status, ORDER BY sort avoidance, table lookup cost, full-scan penalties, additional non-index predicate selectivity, `INDEXED BY`/`NOT INDEXED`, and then applies OR and automatic-index alternatives.

`bestIndex()` chooses between `bestVirtualIndex()` and `bestBtreeIndex()` based on `IsVirtual(pSrc->pTab)`.

`disableTerm()` marks index-satisfied terms as `TERM_CODED` while preserving correctness for LEFT JOIN terms that originated outside the join's ON/USING clause. It also walks parent/child virtual-term relationships so a parent expression is disabled once all children are satisfied.

`codeApplyAffinity()`, `codeEqualityTerm()`, and `codeAllEqualityTerms()` emit VDBE code for equality constraints used by index loops. They handle scalar equality, `IS NULL`, and `IN` loops, allocate registers, apply affinity strings, skip unnecessary affinity conversions, and record IN-loop metadata for `sqlite3WhereEnd()`.

`explainAppendTerm()`, `explainIndexRange()`, and `explainOneScan()` build EXPLAIN QUERY PLAN messages for scan/search choices, including automatic/covering indexes, rowid constraints, virtual-table index numbers/strings, aliases, subqueries, and estimated rows.

`codeOneLoopStart()` emits the actual VDBE loop prefix for one selected `WhereLevel`. It handles virtual tables with `OP_VFilter`/`OP_VNext`, rowid equality with `OP_NotExists`, rowid ranges with seek and end tests, index equality/range scans with `OP_Seek*` and `OP_Idx*` checks, multi-index OR scans with recursive `sqlite3WhereBegin()` calls and `OP_RowSetTest`, and fallback full scans with `OP_Rewind`/`OP_Next` or `OP_Last`/`OP_Prev`. It also emits row predicate tests and LEFT JOIN hit flags.

`sqlite3WhereBegin()` owns the top-level WHERE-loop setup. It allocates `WhereInfo`, `WhereClause`, and `WhereMaskSet`; splits and analyzes WHERE terms; assigns table bitmasks; greedily chooses join order with an "optimal first" pass; enforces `INDEXED BY`; handles one-pass UPDATE/DELETE eligibility; opens table, index, virtual-table, and automatic-index cursors; emits EXPLAIN rows; calls `codeOneLoopStart()` for each loop; and returns the `WhereInfo` consumed by `sqlite3WhereEnd()`.

`sqlite3WhereEnd()` emits loop tails, resolves break/continue labels, unwinds IN loops, synthesizes LEFT JOIN null-row iterations, closes opened cursors, rewrites table `OP_Column`/`OP_Rowid` opcodes into index reads for indexed scans where possible, frees planner state, and restores `pParse->nQueryLoop`.

The parser portion defines small semantic helper types `LimitVal`, `LikeOp`, `TrigEvent`, and `AttachKey`; expression-span helpers `spanSet()`, `spanExpr()`, `spanBinaryExpr()`, `spanUnaryPostfix()`, `binaryToUnaryIfNull()`, and `spanUnaryPrefix()`; generated parser constants (`YYNSTATE`, `YYNRULE`, `YYFALLBACK`, action code ranges, `YYMINORTYPE`); action tables (`yy_action`, `yy_lookahead`, `yy_shift_ofst`, `yy_reduce_ofst`, `yy_default`); fallback-token mappings; `yyStackEntry` and `yyParser`; tracing metadata `yyTokenName[]` and `yyRuleName[]`; parser allocation/free/stack helpers; `yy_destructor()`; `yy_find_shift_action()`; `yy_find_reduce_action()`; `yy_shift()`; `yyRuleInfo[]`; and the start of `yy_reduce()`.

## Control Flow

WHERE analysis starts after the parser has produced a `SrcList`, `Expr *pWhere`, and optional `ExprList *pOrderBy`. `sqlite3WhereBegin()` initializes bitmask state, folds constants, splits the WHERE expression on top-level AND, assigns one bit per FROM term, records which bits represent virtual tables, then calls `exprAnalyzeAll()` so each term can record prerequisite tables and any indexable operator.

`exprAnalyze()` may mutate the working `WhereClause` by appending virtual terms. Column-to-column comparisons get a commuted copy so either side can be considered as an indexed column. BETWEEN adds two child range terms. OR clauses delegate to `exprAnalyzeOrTerm()`, which recursively analyzes OR subclauses and AND subclauses inside OR branches. LIKE/GLOB adds lower and upper string-prefix range terms. MATCH adds a virtual-table constraint term. These child terms use `iParent`, `nChild`, and flags like `TERM_VIRTUAL`, `TERM_DYNAMIC`, `TERM_COPIED`, `TERM_ORINFO`, and `TERM_ANDINFO` to preserve cleanup and disabling semantics.

Plan selection in `sqlite3WhereBegin()` is a loop over desired nesting levels. For each level it tests remaining FROM terms, honoring LEFT JOIN and CROSS JOIN reorder barriers. The first pass looks for "optimal" scans whose chosen plan does not depend on not-yet-ready tables; if none is found, a second pass picks the lowest-cost usable scan. `bestBtreeIndex()` or `bestVirtualIndex()` computes each candidate's `WhereCost`, and the winner becomes the current `WhereLevel`.

For b-tree tables, `bestBtreeIndex()` considers a fake rowid primary-key index first, then real indexes unless `NOT INDEXED` forbids them or `INDEXED BY` fixes a single index. For each candidate it finds contiguous equality/IN terms, at most one range column, possible ORDER BY satisfaction, covering-index status, row estimates, and CPU/search/sort cost. It records flags such as `WHERE_ROWID_EQ`, `WHERE_ROWID_RANGE`, `WHERE_COLUMN_EQ`, `WHERE_COLUMN_RANGE`, `WHERE_COLUMN_IN`, `WHERE_IDX_ONLY`, `WHERE_ORDERBY`, `WHERE_REVERSE`, `WHERE_UNIQUE`, and `WHERE_TEMP_INDEX`.

For virtual tables, `bestVirtualIndex()` creates or reuses one `sqlite3_index_info` per source item, updates per-join-order `usable` flags, clears previous output, calls `xBestIndex`, validates that unusable constraints were not selected, charges extra cost if ORDER BY is not consumed, and stores `WHERE_VIRTUALTABLE` plus `WHERE_ORDERBY` when applicable.

After join order is fixed, `sqlite3WhereBegin()` opens required cursors. Normal tables use `sqlite3OpenTable()` unless an index-only plan can omit the table cursor. Virtual tables use `OP_VOpen`. Real indexes use `OP_OpenRead` with `KeyInfo`. Temporary automatic indexes are constructed by scanning the table once, generating index keys, and inserting them into an autoindex cursor. Schema cookies are verified before and after cursor opening.

`codeOneLoopStart()` then emits one loop per chosen level. It sets break/continue labels, initializes LEFT JOIN match flags, emits the appropriate seek/scan opcodes, and inserts any row-level tests that were not fully satisfied by index constraints. Multi-index OR is special: it recursively calls `sqlite3WhereBegin()` for each OR branch, optionally de-duplicates rowids through a RowSet register, and uses `OP_Gosub`/`OP_Return` to share the parent loop body.

`sqlite3WhereEnd()` emits loop termination in reverse nesting order. It resolves continue labels, emits the saved loop-step opcode, unwinds nested IN iterators, resolves break labels, and generates LEFT JOIN null-row fallback execution when no right-side row matched. It then closes cursors unless the caller requested omission, rewrites table reads to index reads for indexed plans, and frees `WhereInfo`, virtual-table index info, automatic-index objects, and nested WHERE clauses.

The parser flow begins with `sqlite3ParserAlloc()`, then repeated calls to the parser driver outside this chunk push tokens through `yy_shift()` and reduce through `yy_reduce()`. `yy_find_shift_action()` uses `yy_shift_ofst`, `yy_action`, `yy_lookahead`, fallback tokens, wildcard token support, and `yy_default` to pick actions for terminal lookahead. `yy_find_reduce_action()` performs the equivalent lookup for non-terminals after a reduction. If parsing fails or the parser is freed, `yy_destructor()` releases semantic objects that were not consumed into a larger AST.

The covered `yy_reduce()` cases execute early grammar actions: begin EXPLAIN modes, finish code generation at command boundaries, begin/commit/rollback transactions, process savepoints, start and finish CREATE TABLE, add columns/types/defaults/constraints, create primary-key/unique indexes, create foreign keys, create/drop views and tables, build SELECT objects, and link compound SELECTs. Later expression, trigger, pragma, and virtual-table reductions continue past this chunk boundary.

## State And Persistence Behavior

The WHERE planner's main state is transient compile-time state. `WhereClause` owns analyzed `WhereTerm` objects and any dynamically allocated virtual expressions. `WhereInfo` owns the selected `WhereLevel` array, per-level virtual-table index info, automatic-index descriptors, labels/registers used by generated bytecode, and saved query-loop estimate. It is freed by `whereInfoFree()` after `sqlite3WhereEnd()` or on setup error.

Planner bitmasks are central. `WhereMaskSet` maps table cursors to bits; `prereqAll`, `prereqRight`, `notReady`, `notValid`, `used`, and `vmask` decide join dependencies, usable constraints, LEFT JOIN safety, OR-to-IN eligibility, and when row tests can be emitted. The bit assignment invariant that all tables to the left of a FROM term are `(mask - 1)` is required for LEFT JOIN ON-clause handling.

No user table rows are persisted during planning itself, but code generation emits durable operations when the final VDBE is executed. Automatic indexes are transient per statement. They are not database schema objects and are populated into an `OP_OpenAutoindex` cursor at runtime. The planner-generated VDBE may open read or write table cursors depending on one-pass UPDATE/DELETE, but this chunk only generates bytecode; transaction persistence is managed elsewhere.

`sqlite3WhereEnd()` mutates previously emitted VDBE opcodes between `pWInfo->iTop` and the current address. For indexed scans it can replace table-column reads with index-column reads and rowid reads with `OP_IdxRowid`. This is a compile-time bytecode optimization that relies on stable cursor and index-column metadata.

Virtual-table planning state crosses planner/codegen phases through `sqlite3_index_info`. If `xBestIndex` returns an allocated `idxStr`, ownership is tracked by `needToFreeIdxStr`; code generation passes it to `OP_VFilter` using `P4_MPRINTF` or `P4_STATIC` and clears the free flag after handoff. Mismanaging this ownership would leak or double-free parser/VM memory.

STAT2 estimation reads schema statistics already loaded into `Index.aSample` and bound values available during reprepare through `sqlite3VdbeGetValue()`. It does not persist changes; it influences only cost estimates and selected plans. Parameter values used for estimates are marked with `sqlite3VdbeSetVarmask()` so the statement can be reprepared when bindings change.

Parser state is also compile-time. `yyParser` holds the parser stack, error-recovery counter, optional max-depth counter, and the extra `Parse *pParse` argument. `YYMINORTYPE` is a tagged union only by convention; the generated grammar tables and rule actions decide which union member is live for a symbol. Destructors free `Select`, `ExprSpan`, `ExprList`, `SrcList`, `Expr`, `IdList`, `TriggerStep`, and trigger event lists when stack entries are discarded.

The parser semantic actions in this chunk do create persistent schema or transaction effects indirectly by invoking higher-level SQLite routines. For example, transaction grammar actions call transaction APIs, CREATE TABLE/VIEW/index/foreign-key reductions populate schema parse objects and VDBE work, and SELECT reductions allocate `Select` trees or immediately generate output code for top-level SELECT statements. Actual database persistence still occurs later when the VDBE executes.

## Dependencies And Integration Points

The WHERE code depends on expression analysis helpers (`exprTableUsage`, `exprListTableUsage`, `exprSelectTableUsage`, `sqlite3ExprAffinity`, `sqlite3ExprCollSeq`, `sqlite3BinaryCompareCollSeq`, `sqlite3IndexAffinityOk`, `sqlite3CompareAffinity`, `sqlite3ExprNeedsNoAffinityChange`), expression allocation/deletion (`sqlite3ExprDup`, `sqlite3PExpr`, `sqlite3ExprListAppend`, `sqlite3ExprDelete`), and WHERE helpers defined earlier in `where.c` (`whereClauseInit`, `whereSplit`, `whereClauseInsert`, `whereClauseClear`, `findTerm`, `getMask`, `createMask`, `allowedOp`, `operatorMask`, `transferJoinMarkings`).

It integrates with VDBE bytecode generation through many opcodes: `OP_If`, `OP_Integer`, `OP_OpenAutoindex`, `OP_Rewind`, `OP_IdxInsert`, `OP_VOpen`, `OP_VFilter`, `OP_VNext`, `OP_MustBeInt`, `OP_NotExists`, `OP_SeekGt`, `OP_SeekGe`, `OP_SeekLt`, `OP_SeekLe`, `OP_Last`, `OP_Next`, `OP_Prev`, `OP_Rowid`, `OP_Column`, `OP_IdxRowid`, `OP_Seek`, `OP_IdxGE`, `OP_IdxLT`, `OP_RowSetTest`, `OP_Gosub`, `OP_Return`, `OP_NullRow`, `OP_Close`, `OP_Explain`, and `OP_Affinity`.

It also depends on schema/catalog objects (`Table`, `Index`, `Column`, `CollSeq`, `KeyInfo`), source-list metadata (`SrcList_item` fields like `iCursor`, `pTab`, `pIndex`, `notIndexed`, `jointype`, `colUsed`, aliases, subquery ids), parser connection state (`Parse`, `sqlite3`, `pVdbe`, `nMem`, `nTab`, `nQueryLoop`, `nErr`, `mallocFailed`), and compile-time feature gates (`SQLITE_OMIT_OR_OPTIMIZATION`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_BETWEEN_OPTIMIZATION`, `SQLITE_OMIT_LIKE_OPTIMIZATION`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_ENABLE_STAT2`, `SQLITE_OMIT_EXPLAIN`, `SQLITE_TEST`, `SQLITE_DEBUG`).

Virtual-table integration is through the public module API: `sqlite3_index_info`, `sqlite3_index_constraint`, `sqlite3_index_orderby`, `sqlite3_index_constraint_usage`, `sqlite3_vtab`, `xBestIndex`, `idxNum`, `idxStr`, `estimatedCost`, and `orderByConsumed`. The optimizer assumes `WO_*` operator codes match `SQLITE_INDEX_CONSTRAINT_*` constants and asserts that mapping.

ORDER BY and min/max optimization integrate through `ppOrderBy` and `wctrlFlags` values such as `WHERE_ORDERBY_MIN`, `WHERE_ORDERBY_MAX`, `WHERE_ONETABLE_ONLY`, `WHERE_OMIT_OPEN`, `WHERE_OMIT_CLOSE`, `WHERE_FORCE_TABLE`, `WHERE_DUPLICATES_OK`, and `WHERE_ONEPASS_DESIRED`.

The parser section depends on Lemon-generated conventions and SQLite grammar semantic helpers. It integrates with tokenizer token codes, `Parse` state, `Token`, `ExprSpan`, `Select`, `ExprList`, `SrcList`, `IdList`, trigger-step structures, and many schema/codegen functions used in reduction actions. Debug integration is through `sqlite3ParserTrace()`, `yyTokenName[]`, `yyRuleName[]`, and `yytestcase()`.

## Risks And Edge Cases

OR optimization is correctness-sensitive. OR-to-IN conversion must preserve affinity and table/column identity across all OR arms, especially for `t1.a=t2.b` cases with virtual commuted terms. Multi-index OR must avoid duplicate rows unless `WHERE_DUPLICATES_OK` is set and must propagate `untestedTerms` when a recursive OR branch cannot evaluate predicates involving later join tables.

LEFT JOIN handling appears in several places and is easy to regress. `extraRight` prevents ON-clause terms from driving indexes on left-side tables, `disableTerm()` avoids disabling WHERE-clause terms that should filter null-extended rows, `codeOneLoopStart()` records right-table hits, and `sqlite3WhereEnd()` synthesizes null-row iterations. Small changes to prerequisite masks or `EP_FromJoin` checks can produce wrong results.

Automatic indexes are transient but high impact. They must be covering because table and automatic index cannot be kept in sync after the build phase. `constructAutomaticIndex()` must include all referenced columns, skip duplicate equality columns, allocate contiguous `Index` metadata correctly, and emit fill-loop code exactly once per statement execution.

Cost estimates are heuristic and can mis-plan queries. Full scans get a 4x penalty, range constraints use 1/4 selectivity without STAT2, extra equality/range/non-index predicates reduce `nRow` by fixed factors, and `x IN (SELECT ...)` assumes 25 values. These choices affect performance rather than direct correctness, but plan changes can expose latent bugs in codegen paths.

`bestIndex()` for virtual tables frees the `sqlite3_index_info` immediately in its wrapper path, while `sqlite3WhereBegin()` caches per-source `pIdxInfo` for chosen virtual-table plans. Ownership differs by caller path, so edits need to preserve which `sqlite3_index_info` survives to `codeOneLoopStart()`.

Expression affinity/collation handling is a recurring edge case. LIKE range bounds choose `NOCASE` or `BINARY` collation and increment the final prefix byte. Index range bounds and equality keys suppress affinity when conversion would be incorrect. STAT2 string comparisons may allocate UTF-16 conversions. Bugs here can cause missing or extra rows for mixed-type comparisons.

The VDBE rewrite in `sqlite3WhereEnd()` assumes every table column used by an index-only plan appears in the selected index. The assert catches this in debug builds, but in release builds a bad `WHERE_IDX_ONLY` decision could leave invalid table reads or wrong index-column mappings.

Parser tables are generated and dense. Manual edits to `YYNSTATE`, `YYNRULE`, action arrays, fallback mappings, `YYMINORTYPE`, rule names, or `yyRuleInfo[]` can desynchronize parser action lookup from semantic reductions. The chunk already includes a defensive zero-initialization of `yygotominor` because some reduce paths leave it otherwise uninitialized.

Parser destructors must match grammar symbol ownership. If a semantic action consumes a pointer but the destructor still runs on the same stack symbol, it can double-free. If a symbol is missing from `yy_destructor()`, parse errors or stack pops can leak AST objects.

The chunk boundary cuts off `yy_reduce()` mid-switch. Research for later chunks must reconcile subsequent grammar actions, accept/error handling, parser driver entry point, and public parser free/finalization behavior before making file-level conclusions about parser completeness.

## Test Signals

Planner/codegen tests should cover OR-to-IN rewrites, multi-index OR scans over rowid and composite indexes, OR terms containing AND subterms, duplicate suppression through RowSet, and OR branches involving later join tables.

WHERE-term analysis tests should cover column-to-column commutation, BETWEEN virtual range terms, LIKE/GLOB prefix ranges with `BINARY` and `NOCASE` collations, `MATCH` constraints for virtual tables, `IS NULL` on the right side of LEFT JOINs, and STAT2-only `IS NOT NULL` conversion when enabled.

Index planning tests should exercise rowid equality/range, real index equality/range, composite indexes with skipped equality-prefix ORDER BY terms, descending indexes and reverse scans, covering versus non-covering indexes, `INDEXED BY` success/failure, `NOT INDEXED`, unique index row estimates, and ORDER BY elimination.

Automatic-index tests should use joins with no useful persistent index, equality predicates that can drive an index, affinity-incompatible predicates that must not, tables with columns beyond the bitmask cutoff, and statements that execute multiple times to ensure the autoindex initialization guard works.

Virtual-table tests should use custom modules that inspect `xBestIndex` inputs, reject unusable constraints, consume ORDER BY, return allocated and static `idxStr` values, set high estimated costs, and set invalid `argvIndex` values to confirm planner error handling.

LEFT JOIN tests should distinguish terms in ON clauses from terms in WHERE clauses, include indexes on both sides of the join, include null-producing unmatched right rows, and include OR and virtual terms inside the join condition.

VDBE/codegen tests should inspect `EXPLAIN QUERY PLAN` output for SCAN versus SEARCH, automatic covering indexes, rowid constraints, virtual-table indexes, estimated rows, and hidden one-table OR branch explain rows. Runtime tests should also verify IN-loop nesting and NULL handling for index keys.

Parser tests for this chunk should cover EXPLAIN and EXPLAIN QUERY PLAN, BEGIN/COMMIT/ROLLBACK/SAVEPOINT/RELEASE, CREATE TABLE with column and table constraints, defaults with signed literals and identifiers, foreign-key actions and deferrability, CREATE TABLE AS SELECT, CREATE/DROP VIEW, DROP TABLE, simple and compound SELECT, and the early ORDER BY empty-rule case at the chunk boundary.

Error-path tests should include parser stack overflow with a small `YYSTACKDEPTH`, syntax errors that discard partially built SELECT/Expr/ExprList/SrcList/IdList/TriggerStep objects, malloc failures in planner allocation and parser semantic actions, and virtual-table `xBestIndex` returning `SQLITE_NOMEM` or an error message.

### subset-b-008418: lines 89545-96988

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 89545-96988

## Scope And Purpose

This chunk spans several consecutive SQLite amalgamation units in the FoundationDB repository: the tail of generated `parse.c`, all of `tokenize.c`, all of `complete.c`, most of `main.c`, all of `notify.c` behind `SQLITE_ENABLE_UNLOCK_NOTIFY`, and the opening portion of `fts3.c` through the beginning of phrase-position merge logic. The code forms the boundary between SQL text input and SQLite's core runtime APIs, then starts the FTS3/FTS4 virtual-table implementation.

The first section finishes parser reduction actions for common SQL grammar productions. It builds AST objects for `SELECT`, `FROM`, joins, `ORDER BY`, `GROUP BY`, `LIMIT`, DML statements, scalar expressions, `IN`, `BETWEEN`, `CASE`, `CREATE INDEX`, `PRAGMA`, triggers, and `RAISE()`, then closes the LEMON parser driver. These actions do not execute SQL directly; they allocate and link `Expr`, `ExprList`, `Select`, `SrcList`, `IdList`, `TriggerStep`, and related parse structures that later code generation consumes.

The tokenizer section implements SQL token classification, keyword lookup, parser driving, parser cleanup, and SQL completeness checks. It converts SQL bytes into token types, runs the generated parser with a `Parse` context, handles syntax/token errors, enforces SQL-length limits, frees parse-time scratch state, and implements the public `sqlite3_complete()` and `sqlite3_complete16()` APIs.

The main API section initializes and shuts down SQLite process-global subsystems, opens and closes database connections, manages global and per-connection configuration, registers functions/collations/hooks, exposes error/status APIs, drives WAL checkpoint requests, rolls back all btrees for a handle, and implements test-control and file-control entry points. This is the most externally visible part of the chunk.

The unlock-notify section tracks connections blocked on shared-cache locks and schedules callbacks when blocking transactions finish. The FTS3 section introduces the on-disk FTS segment/doclist format, tokenizer/hash APIs, key FTS3 table/cursor/query structs, virtual-table creation/connect/open planning, FTS shadow-table creation, varint/doclist helpers, and segment-interior traversal used to find leaf blocks for a term or prefix.

## Important APIs, Types, And Functions

Parser reduction helpers and generated parser entry points:

- `sqlite3Parser()` is the LEMON parser driver. It shifts/reduces tokens, invokes grammar action cases, handles syntax errors, and accepts or fails the parse.
- Grammar action cases in this range call builders such as `sqlite3ExprListAppend()`, `sqlite3ExprListSetName()`, `sqlite3ExprListSetSpan()`, `sqlite3PExpr()`, `sqlite3Expr()`, `sqlite3SrcListAppendFromTerm()`, `sqlite3SrcListIndexedBy()`, `sqlite3SelectNew()`, `sqlite3DeleteFrom()`, `sqlite3Update()`, `sqlite3Insert()`, `sqlite3CreateIndex()`, `sqlite3Pragma()`, `sqlite3BeginTrigger()`, `sqlite3FinishTrigger()`, and trigger-step constructors.
- Expression actions build `TK_DOT`, `TK_REGISTER`, `TK_VARIABLE`, `TK_CAST`, function calls, infix `LIKE`/`MATCH`, unary/binary operators, `TK_BETWEEN`, `TK_IN`, `TK_SELECT`, `TK_EXISTS`, `TK_CASE`, and `TK_RAISE` nodes. They also preserve token spans for error messages and column aliases.
- Parser error routines `yy_parse_failed()`, `yy_syntax_error()`, and `yy_accept()` close out failed or successful parser states.

Tokenizer and parser-runner APIs:

- `keywordCode()` and `sqlite3KeywordCode()` are generated keyword hash lookups. They map identifier text to parser token codes such as `TK_SELECT`, `TK_JOIN_KW`, `TK_PRAGMA`, `TK_MATCH`, or `TK_ID`.
- `sqlite3GetToken(const unsigned char *z, int *tokenType)` returns the byte length and token type of the next SQL token. It recognizes whitespace/comments, operators, quoted identifiers and strings, numeric literals, bracket identifiers, variables, internal `#NNN` registers, blob literals, identifiers, and keywords.
- `sqlite3RunParser(Parse *pParse, const char *zSql, char **pzErrMsg)` allocates the parser engine, feeds tokens from `sqlite3GetToken()`, appends implicit semicolon and EOF tokens, collects parse errors, deletes invalid VDBEs after top-level parse failure, and frees all parse scratch allocations.
- `sqlite3_complete()` and `sqlite3_complete16()` determine whether a SQL string contains a complete statement. The UTF-8 form is a small state machine with special `CREATE TRIGGER ... END;` handling; the UTF-16 form converts to UTF-8 through a transient `sqlite3_value`.

Core public and private APIs in `main.c`:

- Version and compile-mode APIs: `sqlite3_libversion()`, `sqlite3_sourceid()`, `sqlite3_libversion_number()`, and `sqlite3_threadsafe()`.
- Process lifecycle: `sqlite3_initialize()` initializes mutexes, malloc, global functions, page cache, OS/VFS, and page-cache buffers. `sqlite3_shutdown()` tears down OS, auto-extensions, pcache, malloc, and mutex subsystems.
- Configuration: `sqlite3_config()` mutates `sqlite3GlobalConfig` before initialization. `setupLookaside()` and `sqlite3_db_config()` configure connection lookaside memory. `sqlite3_limit()` returns and optionally changes per-connection limits bounded by `aHardLimit[]`.
- Connection lifecycle: `openDatabase()` backs `sqlite3_open()`, `sqlite3_open_v2()`, and `sqlite3_open16()`. It validates flags, selects mutex behavior, allocates `sqlite3`, initializes schemas/collations/builtins/extensions, opens the main btree, sets defaults, enables lookaside, and configures WAL autocheckpointing. `sqlite3_close()` closes btrees, virtual tables, statements/modules/collations/functions, extensions, lookaside, mutexes, and the database object.
- Transaction cleanup: `sqlite3RollbackAll()` rolls back every attached btree, rolls back virtual-table transactions, expires prepared statements if schema changed, clears deferred constraints, and invokes the rollback hook when applicable. `sqlite3CloseSavepoints()` clears connection-level savepoint structures.
- Function and collation registration: `sqlite3CreateFunc()`, `sqlite3_create_function*()`, `sqlite3_overload_function()`, `createCollation()`, and `sqlite3_create_collation*()` install per-connection `FuncDef` and `CollSeq` entries, manage destructors, and expire active prepared statements as needed.
- Status, hooks, and control APIs: `sqlite3_errmsg*()`, `sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, `sqlite3_progress_handler()`, `sqlite3_interrupt()`, `sqlite3_trace()`, `sqlite3_profile()`, commit/update/rollback hooks, WAL hook/autocheckpoint/checkpoint APIs, `sqlite3_get_autocommit()`, `sqlite3_sleep()`, `sqlite3_extended_result_codes()`, `sqlite3_file_control()`, and `sqlite3_test_control()`.
- Metadata and diagnostics: `sqlite3_table_column_metadata()` is compiled when column metadata is enabled. `sqlite3CorruptError()`, `sqlite3MisuseError()`, and `sqlite3CantopenError()` log source-line diagnostics for breakpoint-friendly error macros.

Unlock-notify APIs:

- `sqlite3_unlock_notify()` registers, cancels, immediately invokes, or rejects unlock-notify callbacks for a blocked connection.
- `sqlite3ConnectionBlocked()`, `sqlite3ConnectionUnlocked()`, and `sqlite3ConnectionClosed()` maintain the process-global blocked connection list and dispatch callbacks.
- `sqlite3BlockedList`, `pBlockingConnection`, `pUnlockConnection`, `xUnlockNotify`, `pUnlockArg`, and `pNextBlocked` are the core state for blocked connections. Access is serialized by `SQLITE_MUTEX_STATIC_MASTER`.

FTS3/FTS4 types and functions:

- `sqlite3_tokenizer_module`, `sqlite3_tokenizer`, and `sqlite3_tokenizer_cursor` define the tokenizer plugin ABI used by FTS tables.
- `Fts3Hash` and `Fts3HashElem` define a standalone hash table used by FTS3 for tokenizer registries and pending terms.
- `Fts3Table` is the virtual table instance. It stores the owning `sqlite3 *`, database/table names, user columns, tokenizer, cached statements, expression lists for compressed/uncompressed content access, node/page sizing, shadow-table capability flags, an optional `%_segments` blob handle, and pending terms buffered during transactions.
- `Fts3Cursor` stores the virtual table cursor state, including selected search strategy, current SQL statement, MATCH expression tree, doclist cursor state, deferred tokens, and matchinfo buffers.
- `Fts3PhraseToken`, `Fts3Phrase`, and `Fts3Expr` model MATCH query tokens, phrases, NEAR/AND/OR/NOT trees, loaded doclists, and current docid positions.
- `sqlite3Fts3PutVarint()`, `sqlite3Fts3GetVarint()`, `sqlite3Fts3GetVarint32()`, and `sqlite3Fts3VarintLen()` implement FTS3's little-endian varint encoding, distinct from SQLite btree varints.
- `sqlite3Fts3Dequote()`, `fts3GetDeltaVarint()`, `fts3GetDeltaVarint2()`, `fts3PutDeltaVarint()`, `fts3PoslistCopy()`, `fts3ColumnlistCopy()`, `fts3ReadNextPos()`, `fts3PutColNumber()`, `fts3PoslistMerge()`, and the beginning of `fts3PoslistPhraseMerge()` manipulate FTS doclist/position-list encodings.
- `fts3DisconnectMethod()`, `fts3DestroyMethod()`, `fts3DeclareVtab()`, `fts3CreateTables()`, `fts3DatabasePageSize()`, `fts3InitVtab()`, `fts3ConnectMethod()`, `fts3CreateMethod()`, `fts3BestIndexMethod()`, `fts3OpenMethod()`, `fts3CloseMethod()`, and `fts3CursorSeek()` implement early FTS3 virtual-table lifecycle, planning, cursor, and content-row seek behavior.
- `fts3ScanInteriorNode()` and `fts3SelectLeaf()` traverse serialized segment interior nodes to identify leaf block ranges that may contain a term or term prefix.

## Control Flow

SQL parsing begins with `sqlite3RunParser()`. It initializes `pParse`, allocates the LEMON parser, temporarily enables lookaside allocations when available, and loops over the SQL text. Each iteration calls `sqlite3GetToken()`, advances by the returned length, enforces `SQLITE_LIMIT_SQL_LENGTH`, ignores spaces/comments except for interrupt polling, reports `TK_ILLEGAL` tokens immediately, and sends all ordinary tokens to `sqlite3Parser()`. If the input ends without syntax or runtime parse error, it injects a semicolon if needed and then EOF token `0`.

`sqlite3GetToken()` is a switch-driven scanner. Single-character and two-character operators are returned directly; `--` and `/*...*/` comments become `TK_SPACE`; quote-delimited strings and identifiers are scanned with doubled-quote escaping; numeric tokens are classified as integer or float and become illegal if followed by identifier characters; bind parameters can be `?NNN`, `$name`, `@name`, `:name`, and Tcl-style `$name(...)`; `#NNN` is treated as an internal register reference for nested parses. Unquoted identifiers are handed to `keywordCode()`, which uses generated compact arrays and case-insensitive comparison to avoid a general-purpose hash table.

Generated parser reductions build tree state bottom-up. For example, `FROM` terms accumulate in `SrcList`, join modifiers flow through `sqlite3JoinType()` and `sqlite3SrcListShiftJoinType()`, sort/group/expression lists accumulate through `ExprList`, and DML/DDL grammar rules dispatch to higher-level parse routines. `IN ()` is simplified during parsing into constant true/false depending on `NOT`; `IN (SELECT ...)` and scalar subqueries set `EP_xIsSelect`; function calls enforce the per-connection function-argument limit; trigger grammar rejects qualified target table names and `INDEXED BY` inside trigger DML.

Parser shutdown is centralized in `sqlite3RunParser()`. It exports parse error text through `pzErrMsg`, logs parse errors, deletes an invalid top-level VDBE when parsing failed, releases shared-cache table locks and virtual-table locks, deletes partially constructed tables/triggers unless ownership has moved to virtual-table declaration code, frees variable-expression arrays and aliases, drains autoincrement and zombie-table lists, restores the saved lookaside state, and normalizes the return code.

`sqlite3_complete()` does not invoke the full parser. It tokenizes just enough to recognize semicolon completion and trigger bodies. With triggers enabled, it uses an eight-state transition table over `SEMI`, whitespace, ordinary tokens, `EXPLAIN`, `CREATE`, `TEMP`, `TRIGGER`, and `END`. It returns true only in the `START` state after at least one complete statement. Unterminated comments, quoted identifiers, strings, and bracket identifiers return false.

`sqlite3_initialize()` first initializes WSD if needed, then returns immediately if `isInit` is already true. Otherwise it initializes the mutex subsystem, uses the static master mutex to initialize malloc and allocate a recursive init mutex, enters the recursive init mutex to register global SQL functions, initialize pcache, initialize OS/VFS, install page-cache buffers, and finally set `isInit`. The recursive mutex allows `sqlite3_os_init()` paths to call back into initialization safely. Afterward, the temporary init mutex is freed when its reference count drops to zero.

`openDatabase()` is the central connection-open path. It autoinitializes SQLite, rejects nonsensical open flag combinations, derives thread-safety and shared-cache flags, masks internal-only flags, allocates the `sqlite3` object and optional recursive mutex, initializes limits and defaults, registers built-in collations, resolves the VFS, opens the main btree, obtains schemas, registers built-in functions and automatic extensions, initializes optional extensions such as FTS3/ICU/RTREE, sets default locking mode, configures lookaside, and installs the default WAL autocheckpoint hook. On error it keeps a "sick" handle for many errors but fully closes and nulls the handle on `SQLITE_NOMEM`.

`sqlite3_close()` enters the connection mutex, resets schema state, rolls back virtual-table transactions, rejects close while VDBEs or backup operations remain active, closes savepoints and all btrees, resets schemas again, notifies unlock-notify code that the connection is gone, destroys function/collation/module registrations with their destructors, clears error objects and extensions, frees temp schema and lookaside memory, destroys the mutex, marks the handle closed, and frees `sqlite3`.

`sqlite3_wal_checkpoint_v2()` validates checkpoint mode, resolves a named attached database if supplied, and delegates to `sqlite3Checkpoint()`. `sqlite3Checkpoint()` iterates either one database or all attached databases, calls `sqlite3BtreeCheckpoint()`, and converts any encountered per-btree `SQLITE_BUSY` into a final `SQLITE_BUSY` after continuing through eligible databases.

Unlock-notify flow begins when `sqlite3ConnectionBlocked()` records that a connection is blocked by another and adds it to `sqlite3BlockedList`. `sqlite3_unlock_notify()` either cancels state, immediately invokes the callback if there is no blocker, rejects deadlock when following `pUnlockConnection` reaches the registering connection, or records the callback and groups the connection in the blocked list by callback pointer. `sqlite3ConnectionUnlocked()` scans the blocked list when a transaction releases locks, clears blocker references, batches callback arguments for matching callback functions, grows the argument array when needed, invokes callbacks, and removes entries with no remaining block/unlock relation.

FTS3 virtual-table creation and connection flow goes through `fts3InitVtab()`. It parses module arguments, initializes a tokenizer from `tokenize=...` or the default `simple` tokenizer, interprets FTS4 options such as `matchinfo=fts3`, `compress=...`, and `uncompress=...`, derives column names, allocates a single `Fts3Table` block holding struct, column pointer array, table/database names, and copied column-name strings, validates paired compression options, builds read/write expression lists, creates shadow tables for `xCreate`, reads database page size for cost estimates, and declares the virtual table schema with hidden MATCH and `docid` columns. On failure it destroys either the partially built table or tokenizer.

FTS3 planning in `fts3BestIndexMethod()` chooses among full scan, rowid/docid lookup, and MATCH search. It defaults to a costly full scan, lowers cost for rowid/docid equality, and prefers the first usable MATCH constraint over rowid lookup so the core will not leave MATCH as an unusable scalar function. The selected constraint is assigned `argvIndex = 1` and marked omitted.

FTS3 segment lookup uses serialized interior nodes. `fts3ScanInteriorNode()` skips height and leftmost child varints, reconstructs delta-encoded separator terms into a growable buffer, compares each separator with the requested term, and returns first/last child blockids that can contain the exact term or prefix range. `fts3SelectLeaf()` reads child interior blocks through `sqlite3Fts3ReadBlock()` and recurses until leaf-level blockids are selected.

FTS3 doclist helpers operate on tightly packed buffers. Delta varints encode increasing docids or positions. Position lists are terminated by `POS_END` and column changes by `POS_COLUMN`. `fts3PoslistCopy()` advances and optionally copies an entire position list, `fts3ColumnlistCopy()` handles one column list without copying the terminator, `fts3PoslistMerge()` merges two position lists by column and by sorted positions while suppressing duplicates, and `fts3PutColNumber()` emits nonzero column headers.

## State And Persistence Behavior

Parser and tokenizer state is transient. `sqlite3RunParser()` mutates `Parse`, temporary AST allocations, temporary VDBE state, `db->lookaside.bEnabled`, `db->u1.isInterrupted`, and error fields. It does not persist database changes by itself. Persistence occurs later when parse routines generate VDBE programs and those programs execute.

`sqlite3_complete()` has no durable side effects. It scans input and returns a boolean based on its local state machine. `sqlite3_complete16()` allocates a temporary `sqlite3_value`, converts the string, and frees it before return.

Global SQLite state is persistent for the process. `sqlite3_initialize()` mutates `sqlite3GlobalConfig` subsystem flags, mutex pointers, registered global functions, page-cache configuration, and VFS/OS state. `sqlite3_shutdown()` clears those same process-global subsystems and must only be called when SQLite is otherwise unused.

Connection state is durable for the lifetime of `sqlite3 *`. `openDatabase()` initializes limits, flags, default schemas, function/collation registries, btree pointers, lookaside buffers, hooks, and extension state. `sqlite3_close()` tears all of this down. `setupLookaside()` may free a previous lookaside buffer and install a caller-supplied or malloc-owned replacement; it refuses changes while lookaside allocations are outstanding.

Disk persistence in this chunk is mostly indirect. `openDatabase()` opens the main btree file and may create or initialize extension state, but it does not necessarily write schema data. `sqlite3RollbackAll()` rolls back btree and virtual-table transactions, which reverts durable changes made elsewhere. WAL checkpoint APIs can persist checkpoint progress by delegating to btree/pager/WAL layers. `sqlite3_file_control()` may invoke VFS-specific operations that can mutate file-control state outside SQLite's portable abstraction.

Function and collation registration persist in the connection's in-memory registries. Replacing an existing function or collation expires prepared statements if no VM is active, and returns `SQLITE_BUSY` if active VMs would make replacement unsafe. Registered destructors are retained and invoked only when the final function copy or collation registration is destroyed or replaced.

Error and hook state lives on the connection. Busy, progress, trace, profile, commit, update, rollback, WAL, collation-needed, and extended-result-code APIs install callback pointers and callback arguments under the connection mutex. `sqlite3_interrupt()` sets `db->u1.isInterrupted`, which the parser notices while consuming whitespace and VDBE execution paths observe elsewhere.

Unlock-notify state is process-global plus per-connection. The blocked-list links and callback state are memory-only and protected by the static master mutex. `sqlite3ConnectionClosed()` releases callbacks and removes a closing connection so no later unlock dispatch references freed memory.

FTS3 `xCreate` persists five possible shadow tables: `%_content`, `%_segments`, `%_segdir`, and for FTS4 `%_docsize` and `%_stat`. `xDestroy` drops those tables. `Fts3Table.pendingTerms` buffers transaction-local index updates in memory until flush paths outside this chunk create new segment rows. Segment/doclist helpers define the durable binary format stored in `%_segments`, `%_segdir.root`, and doclist blobs.

## Dependencies And Integration Points

The parser reduction code depends on parser token definitions, AST structures, allocation helpers, expression/list/source builders, DML/DDL parse routines, trigger constructors, and VDBE generation later in the pipeline. It is generated from SQLite grammar but embedded directly in the amalgamation.

Tokenizer and parser-runner code integrates with character classification tables (`sqlite3CtypeMap`, `sqlite3UpperToLower`, EBCDIC maps), keyword token constants, `sqlite3ParserAlloc()`, `sqlite3ParserFree()`, `sqlite3Parser()`, parse error helpers, lookaside allocation, shared-cache table-lock cleanup, virtual-table lock cleanup, autoincrement bookkeeping, and statement deletion.

Main API code integrates with nearly every SQLite subsystem: mutex, malloc, scratch/pagecache, OS/VFS, btree, pager, WAL, schema, virtual tables, extension autoloading, FTS/ICU/RTREE optional modules, collation/function lookup, prepared statement invalidation, error reporting, test hooks, and file-control dispatch.

`openDatabase()` calls `sqlite3BtreeOpen()` for the main database, `sqlite3SchemaGet()` for main and temp schemas, `sqlite3RegisterBuiltinFunctions()`, `sqlite3AutoLoadExtensions()`, optional `sqlite3Fts3Init()`, `sqlite3IcuInit()`, and `sqlite3RtreeInit()`, then `setupLookaside()` and `sqlite3_wal_autocheckpoint()`. This makes it the registration point for several compile-time feature modules covered later in the file.

WAL functions integrate with btree checkpointing through `sqlite3BtreeCheckpoint()`, and with commit-time WAL hooks through `db->xWalCallback` and `sqlite3WalDefaultHook()`. Busy handlers depend on the VFS `xSleep` implementation through `sqlite3OsSleep()`.

Unlock-notify depends on shared-cache lock conflict paths setting `db->pBlockingConnection` through `sqlite3ConnectionBlocked()`, and on transaction close paths calling `sqlite3ConnectionUnlocked()`. It is compiled only when `SQLITE_ENABLE_UNLOCK_NOTIFY` is enabled.

FTS3 integrates with SQLite's virtual-table module API (`sqlite3_vtab`, `sqlite3_vtab_cursor`, `sqlite3_index_info`, `sqlite3_declare_vtab()`), tokenizer registration (`sqlite3Fts3InitTokenizer()` and tokenizer modules), SQL execution (`sqlite3_exec`, `sqlite3_prepare`, `sqlite3_step`, `sqlite3_finalize`), blob/statement APIs, shadow tables, and later FTS3 read/write/query modules declared in this chunk (`sqlite3Fts3UpdateMethod()`, `sqlite3Fts3PendingTermsFlush()`, `sqlite3Fts3SegReader*()`, `sqlite3Fts3Expr*()`, snippet/offset/matchinfo functions).

## Risks And Edge Cases

The parser action section is generated, dense, and type-indexed through `yygotominor`/`yymsp` union fields. Edits are risky unless regenerated from grammar, because one wrong minor-type assumption can corrupt parse state. The chunk also contains many ownership transfers; failed allocation paths rely on later parser cleanup to free partially built structures.

`sqlite3GetToken()` must avoid overreading while classifying malformed input. It returns `TK_ILLEGAL` for unterminated quotes, malformed blob literals, variables with no name, numeric literals followed by identifier characters, and unsupported characters. Changes to identifier rules can affect keyword recognition, bind parameter parsing, and `sqlite3_complete()` consistency.

`sqlite3RunParser()` temporarily changes `db->lookaside.bEnabled`. Any future early return must restore it and free the parser engine. The current implementation funnels through cleanup, but maintenance edits in this function can easily create leaks of `pParse->pNewTable`, trigger state, table locks, virtual-table locks, alias arrays, autoincrement info, or zombie tables.

`sqlite3_complete()` is intentionally approximate and independent of the full parser. Its quote handling scans to the next matching quote and does not implement doubled quote escaping like `sqlite3GetToken()` does. It is designed for statement-boundary detection, so tests should not assume full syntax validation.

`sqlite3_initialize()` and `sqlite3_shutdown()` are process-global and have strict call-order assumptions. Calling `sqlite3_config()` after initialization returns misuse. Calling shutdown while connections, memory allocations, or threads are active is documented unsafe. Recursive initialization relies on `inProgress`, `pInitMutex`, and reference counting remaining consistent.

`openDatabase()` returns a non-null sick handle for many open failures. Callers must inspect the return code and may still need to close the handle. The function also masks unsupported open flags silently after validating the access-mode combination, which can surprise callers expecting all flag bits to be honored.

Function and collation replacement is blocked while VMs are active, but only when replacing an existing matching entry. Destructor reference counts are subtle when `SQLITE_ANY` creates multiple encoded variants. A destructor passed to `sqlite3_create_function_v2()` is invoked immediately on allocation failure or later when the final function copy is destroyed.

`sqlite3_close()` returns `SQLITE_BUSY` if statements or backups remain. It also rolls virtual-table state before checking active statements so virtual table implementations can release internally held statements. Tests should cover both user-visible busy cases and cleanup after modules with `xDestroy` callbacks.

`sqlite3CorruptError()` in this FoundationDB copy prints directly with `printf("database corruption line %d\n", lineno)` in addition to `sqlite3_log()`. That is unusual for SQLite library code and can leak diagnostics to stdout in embedders.

Unlock-notify invokes callbacks while holding the static master mutex in this version. Callback implementations must avoid re-entering APIs that could deadlock on the same global mutex. The code has special handling for OOM while growing the callback-argument array, but it can split one logical callback group into multiple invocations.

FTS3 varint parsing assumes buffers are valid enough for the caller's context. Some comments document padding guarantees for segment blocks, but corruption can still return `SQLITE_CORRUPT` only after partial decoding. Position-list routines such as `fts3PoslistCopy()` and `fts3ColumnlistCopy()` rely on well-formed terminators and are unsafe for arbitrary untrusted buffers without surrounding integrity checks.

FTS3 `fts3InitVtab()` parses `tokenize` by checking the first eight bytes and then passes `&z[9]`, assuming the ninth character separates the option name and tokenizer arguments. Option syntax changes can break compatibility. FTS4 compression options must be paired; missing `compress` or `uncompress` is a hard constructor error.

FTS3 `xConnect()` in this chunk does not verify that shadow tables already exist; the comment marks this as a TODO. A malformed schema can therefore connect successfully and fail later during reads or writes.

## Test Signals

Parser/tokenizer tests should cover all token classes in `sqlite3GetToken()`: comments as whitespace, nested-looking but non-nested C comments, doubled quotes in string and identifier tokens, unterminated quotes, numeric integer/float/exponent forms, invalid numeric suffixes, blob literal even-length enforcement, `?NNN`/`$name`/`@name`/`:name` variables, internal `#NNN` registers in nested and non-nested parses, bracket identifiers, and all generated keywords exposed through `sqlite3KeywordCode()`.

SQL parse tests should exercise the grammar actions present in this range: joins with `ON` and `USING`, table and subquery `FROM` terms, `ORDER BY` sort directions, `GROUP BY`/`HAVING`, both `LIMIT ... OFFSET ...` syntaxes, `DELETE`, `UPDATE`, `INSERT ... VALUES`, `INSERT ... SELECT`, `DEFAULT VALUES`, collations, casts, function calls with too many args, empty `IN ()` and `NOT IN ()`, subquery `IN`, `EXISTS`, `CASE`, `CREATE INDEX`, `PRAGMA` forms, trigger creation, trigger DML restrictions, and `RAISE()`.

Completeness tests should include whitespace-only strings, ordinary semicolon-terminated statements, statements with semicolons inside strings/comments/quoted identifiers, unterminated comments/quotes, `EXPLAIN CREATE TEMP TRIGGER ... BEGIN ...; END;`, and builds with `SQLITE_OMIT_TRIGGER`.

Core API tests should verify initialization idempotence, shutdown after initialization, rejection of `sqlite3_config()` after initialization, legal and illegal `sqlite3_open_v2()` flag combinations, sick-handle behavior on open errors, lookaside reconfiguration returning `SQLITE_BUSY` while slots are checked out, limit clamping to hard limits, close returning `SQLITE_BUSY` for unfinalized statements and unfinished backups, rollback-hook behavior in `sqlite3RollbackAll()`, and destructor behavior for functions/collations.

WAL and hook tests should cover `sqlite3_wal_autocheckpoint()` installing and disabling the default hook, invalid checkpoint modes returning misuse, unknown database names returning error, all-database checkpoint iteration, and `SQLITE_BUSY` propagation when one checkpoint target is busy. Busy-timeout tests should validate retry counts and timeout boundaries with the configured VFS sleep path.

Error API tests should cover null handles, sick handles, malloc-failure paths in `sqlite3_errmsg()` and `sqlite3_errmsg16()`, extended result-code masking, `sqlite3_interrupt()` visibility during parse and execution, and `sqlite3_file_control()` for unknown database names, null btrees, `SQLITE_FCNTL_FILE_POINTER`, VFS-handled controls, and no-method `SQLITE_NOTFOUND`.

Unlock-notify tests should require shared-cache builds. They should cover immediate callback when no blocker remains, replacing a prior callback on the same connection, cancellation with `xNotify == NULL`, deadlock detection through blocker chains, grouped callback delivery for same `xUnlockNotify`, closing a blocked or blocking connection, and OOM simulation while growing the callback argument array.

FTS3/FTS4 tests should create FTS3 and FTS4 tables with default and explicit tokenizers, quoted column names, no explicit columns, `matchinfo=fts3`, paired and unpaired `compress`/`uncompress`, and verify shadow-table creation/destruction. Query-planner tests should inspect `xBestIndex` choices for full scan, docid equality, column MATCH, table-wide MATCH, unusable constraints, and MATCH preferred over docid equality when both are present.

FTS3 format tests should round-trip `sqlite3Fts3PutVarint()`/`sqlite3Fts3GetVarint()` across boundary values, decode invalid or truncated segment interiors as corruption where checked, verify `fts3SelectLeaf()` leaf ranges for exact and prefix searches across multi-level segment trees, and validate position-list union/phrase merge behavior across columns, duplicate positions, empty lists, and terminators.

### subset-b-008419: lines 96989-105142

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 96989-105142

## Scope And Purpose

This chunk covers a large contiguous part of SQLite's FTS3/FTS4 implementation in the FoundationDB-contrib SQLite amalgamation. It begins in the position-list phrase merge helper, then implements FTS3 doclist merging and query evaluation, the `fts3`/`fts4` virtual-table method table, tokenizer registration, the `fts4aux` statistics virtual table, the MATCH-expression parser, FTS3's standalone hash table, the simple and porter tokenizers, most of the FTS3 write/segment merge machinery, deferred-token handling, `xUpdate`/`optimize`, and the opening definitions for snippet, offsets, and matchinfo processing.

The central theme is the full-text index lifecycle: parse a MATCH expression, tokenize input text, read and merge compressed doclists from pending terms and `%_segments`/`%_segdir`, evaluate boolean/phrase/NEAR constraints, expose auxiliary SQL functions and `fts4aux`, and update persistent FTS shadow tables on INSERT/UPDATE/DELETE/optimize.

## Important APIs, Types, And Functions

`fts3PoslistPhraseMerge()`, completed at the start of this chunk, and `fts3PoslistNearMerge()` operate on FTS3 position lists. They compare column-aware delta-encoded token positions, preserve or discard left/right positions depending on caller needs, and implement phrase and bidirectional NEAR matching.

`fts3DoclistMerge()` is the main compressed doclist combiner. It supports `MERGE_OR`, `MERGE_POS_OR`, `MERGE_AND`, `MERGE_NOT`, `MERGE_PHRASE`, `MERGE_POS_PHRASE`, `MERGE_NEAR`, and `MERGE_POS_NEAR`. It reads delta-varint docids from two sorted input doclists, writes delta-varint output to a caller-provided buffer, and optionally counts result documents.

`TermSelect` plus `fts3TermSelectCb()`, `fts3TermSelectMerge()`, `sqlite3Fts3SegReaderCursor()`, `fts3TermSegReaderCursor()`, and `fts3TermSelect()` retrieve all segment doclists for a term or prefix. They combine pending terms with on-disk segment readers, configure `Fts3SegFilter`, optionally apply column filters and position requirements, and merge multiple matching segment doclists into one result.

`fts3PhraseSelect()`, `fts3EvalExpr()`, `fts3NearMerge()`, and `sqlite3Fts3ExprNearTrim()` evaluate phrase and expression nodes. Phrase evaluation may process tokens in cheapest-first order during `xFilter()`, defer common tokens, merge multi-token phrases by position distance, and retain positions for NEAR, snippet, offsets, or matchinfo consumers.

`fts3FilterMethod()`, `fts3NextMethod()`, `fts3EofMethod()`, `fts3RowidMethod()`, `fts3ColumnMethod()`, `fts3UpdateMethod()`, transaction hooks, `fts3FindFunctionMethod()`, and `fts3RenameMethod()` form the `fts3Module` `sqlite3_module`. `sqlite3Fts3Init()` registers the `fts3` and `fts4` modules, initializes tokenizer hash state, registers `fts4aux`, and overloads `snippet`, `offsets`, `matchinfo`, and `optimize`.

`Fts3auxTable` and `Fts3auxCursor` implement the `fts4aux` virtual table with schema `term, col, documents, occurrences`. Its cursor reuses FTS segment readers and computes per-term aggregate and per-column document/occurrence counts by decoding position-bearing doclists.

The parser section defines `ParseContext`, `getNextToken()`, `getNextString()`, `getNextNode()`, `insertBinaryOperator()`, `fts3ExprParse()`, `sqlite3Fts3ExprParse()`, and `sqlite3Fts3ExprFree()`. It handles legacy and parenthesized FTS3 syntax, column qualifiers, quoted phrases, prefix tokens, implicit AND, OR/AND/NOT/NEAR precedence, and `NEAR/N` distance arguments.

The hash section defines the FTS3-local `Fts3Hash` operations: `sqlite3Fts3HashInit()`, `sqlite3Fts3HashClear()`, `sqlite3Fts3HashFindElem()`, `sqlite3Fts3HashFind()`, and `sqlite3Fts3HashInsert()`. It supports string or binary keys, optional key copies, bucket rehashing, and a global insertion-order list.

The tokenizer sections implement `porterTokenizerModule` and `simpleTokenizerModule`. The porter tokenizer scans non-delimiter runs, case-folds ASCII, applies a Porter stemmer for short alphabetic words, and falls back to truncating/copying for unsuitable terms. The simple tokenizer lowercases ASCII and treats configured or default non-alphanumeric ASCII bytes as delimiters.

The write section defines persistent indexing structures and helpers: `PendingList`, `Fts3DeferredToken`, `Fts3SegReader`, `SegmentWriter`, and `SegmentNode`; SQL statement ids for shadow-table operations; `fts3SqlStmt()`, `fts3SqlExec()`, `sqlite3Fts3ReadLock()`, `sqlite3Fts3AllSegdirs()`, pending-list append/add helpers, `fts3InsertTerms()`, `fts3InsertData()`, `fts3DeleteAll()`, `fts3DeleteTerms()`, segment readers/writers, `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, `sqlite3Fts3SegReaderFinish()`, `fts3SegmentMerge()`, `sqlite3Fts3PendingTermsFlush()`, docsize/stat encoders, `sqlite3Fts3UpdateMethod()`, and `sqlite3Fts3Optimize()`.

The snippet opening defines matchinfo format flags (`p`, `c`, `n`, `a`, `l`, `s`, `x`), `LoadDoclistCtx`, `SnippetIter`, `SnippetPhrase`, `SnippetFragment`, `MatchInfo`, `StrBuffer`, `fts3GetDeltaPosition()`, and `fts3ExprIterate()`. The actual snippet/matchinfo algorithms continue after this chunk.

## Control Flow

Query execution starts in `fts3FilterMethod()`. For full-text searches, it parses the MATCH argument with `sqlite3Fts3ExprParse()`, obtains a content-table read lock, evaluates the expression into a docid doclist with `fts3EvalExpr()`, closes any segment blob handle, prepares a content-row lookup statement, and calls `fts3NextMethod()`. Full scans prepare a `%_content` scan; docid lookups bind one rowid.

`fts3EvalExpr()` recursively evaluates expression trees. Phrase nodes call `fts3PhraseSelect()`. OR allocates a combined output and uses `MERGE_OR`; AND and NOT merge bare docid lists in-place; NEAR first forces position-bearing phrase lists, then calls `fts3NearMerge()`. In filter mode, AND subexpressions are costed through segment-reader cost estimates and processed cheapest first. If the next token/subexpression appears more expensive than the already narrowed doclist, the evaluator marks tokens deferred and returns a superset.

Deferred evaluation runs in `fts3NextMethod()` through `fts3EvalDeferred()`. If a filter-time result was a superset, the current content row is sought, deferred doclists are rebuilt for that single row by retokenizing its columns in `sqlite3Fts3CacheDeferredDoclists()`, and `fts3EvalExpr()` is rerun in `FTS3_EVAL_NEXT` mode to decide whether to accept the row.

Term selection creates a `Fts3SegReaderCursor` over pending terms and/or `%_segdir` rows. `sqlite3Fts3SegReaderCursor()` optionally adds a pending-terms reader, scans selected segment-directory rows, narrows leaf ranges with `fts3SelectLeaf()` for bounded term searches, and allocates one `Fts3SegReader` per segment. `sqlite3Fts3SegReaderStart()` advances each reader to the filter term and sorts readers by term/age. `sqlite3Fts3SegReaderStep()` groups readers on the same term, merges their doclists by docid, applies column filtering and position stripping as requested, and returns `SQLITE_ROW` for each merged term.

The parser is hand-written. `getNextNode()` tokenizes operators, parentheses, quoted strings, and single tokens. `fts3ExprParse()` repeatedly inserts phrase and operator nodes into a tree using `insertBinaryOperator()`, adds implicit AND nodes when adjacent phrases occur, handles legacy `-token` as NOT branches, rejects NEAR operands that are not phrases, and reports mismatched parentheses from the public wrapper.

Updates flow through `sqlite3Fts3UpdateMethod()`. Deletes or updates first check whether removing the row empties the table. If so, all FTS shadow tables and pending terms are cleared. Otherwise the old row is tokenized with column `-1` to append delete markers into pending terms, content/docsize rows are deleted, and document totals are decremented. Inserts write `%_content`, advance or flush pending terms if docids are out of order or memory is high, tokenize inserted columns into pending lists, optionally write `%_docsize`, and update `%_stat` totals.

Pending terms are flushed by `sqlite3Fts3PendingTermsFlush()`, which calls `fts3SegmentMerge()` with `FTS3_SEGCURSOR_PENDING`. Segment merging opens readers for the requested level or all levels, streams merged term/doclists through `sqlite3Fts3SegReaderStep()`, feeds them to `fts3SegWriterAdd()`, deletes old `%_segments`/`%_segdir` rows or clears pending terms, and writes the replacement segment with `fts3SegWriterFlush()`.

Segment writing batches prefix-compressed term/doclist records into leaf blocks of `p->nNodeSize`. When a leaf fills, `fts3SegWriterAdd()` writes it to `%_segments` and inserts a separator term into an in-memory `SegmentNode` tree. `fts3NodeWrite()` later writes interior nodes bottom-up into `%_segments`, except for the root, which is stored inline in the `%_segdir.root` blob. Single-leaf segments store the whole root directly in `%_segdir`.

The `fts4aux` cursor starts with `fts3auxFilterMethod()`, configures an exact or range scan filter, opens a segment reader cursor, then uses `fts3auxNextMethod()` to parse each term's merged position doclist. A small state machine counts document boundaries, column markers, and positions into `aStat[0]` for all columns and `aStat[i+1]` for individual columns, yielding one row for `*` plus one row per column that has documents.

## State And Persistence Behavior

FTS3 persistent state lives in shadow tables. `%_content` stores row text by docid, `%_segments` stores segment b-tree blocks keyed by blockid, `%_segdir` stores segment metadata and inline roots, `%_docsize` stores per-row encoded column token counts when enabled, and `%_stat` stores record 0 with total rows, per-column token totals, and total byte size when enabled.

Pending indexing state is in `Fts3Table.pendingTerms`, a hash from term bytes to `PendingList`. A `PendingList` stores delta-encoded docids, column markers, positions, and zero terminators in memory until flush. `p->iPrevDocid` and `p->nPendingData` enforce monotonically increasing pending docids and trigger flushes when docids go backwards or pending data exceeds `nMaxPendingData`.

Doclists and position lists are compact binary formats. Docids are stored as delta varints. Position-list entries encode position deltas plus two; `0x00` terminates a doclist entry's positions, and `0x01` introduces a new column number. Many functions mutate cursor pointers in-place while reading these lists, so ownership and pointer advancement are part of the API contract.

Segment readers may own heap-allocated node buffers, point at inline root-node memory immediately after the reader object, or iterate directly over pending-term hash entries. `sqlite3Fts3ReadBlock()` reuses `Fts3Table.pSegments`, an open incremental blob handle on `%_segments.block`; callers that can return to SQLite user code close it with `sqlite3Fts3SegmentsClose()` to release locks.

Segment writers accumulate transient leaf buffers and an in-memory interior tree before persisting blocks. On successful flush, durable changes are `%_segments` inserts and a `%_segdir` insert. Merges delete obsolete segment blocks and directory rows only after the replacement writer has collected merged term data, but the surrounding SQLite transaction provides atomicity.

Deferred token state is cursor-local. `sqlite3Fts3DeferToken()` links `Fts3DeferredToken` objects from phrase tokens to `Fts3Cursor.pDeferred`; `sqlite3Fts3CacheDeferredDoclists()` materializes row-local pending lists for the current row; `sqlite3Fts3FreeDeferredDoclists()` clears cached lists and loaded expression doclists; `sqlite3Fts3FreeDeferredTokens()` frees the token records.

Auxiliary functions receive the active FTS cursor through the hidden column whose name matches the table. `fts3ColumnMethod()` returns a blob containing the `Fts3Cursor *`; `fts3FunctionArg()` validates and extracts it for `snippet`, `offsets`, `matchinfo`, and `optimize`.

Tokenizer registration state is connection-local in an `Fts3Hash` stored as module auxiliary data. `sqlite3Fts3InitHashTable()` exposes it through the `fts3_tokenizer()` scalar function, and `hashDestroy()` frees it when the module is destroyed.

## Dependencies And Integration Points

This code depends heavily on SQLite core virtual-table APIs (`sqlite3_module`, `xFilter`, `xNext`, `xColumn`, `xUpdate`, `sqlite3_create_module_v2`, `sqlite3_overload_function`), SQL statement APIs, incremental blob APIs, SQLite memory allocation, `sqlite3_value`/`sqlite3_context`, and the FTS tokenizer interface (`sqlite3_tokenizer_module`).

The read/query path integrates with earlier FTS3 structures and helpers defined outside this range, including `Fts3Table`, `Fts3Cursor`, `Fts3Expr`, `Fts3Phrase`, `Fts3PhraseToken`, `Fts3SegReaderCursor`, `Fts3SegFilter`, `fts3BestIndexMethod()`, `fts3ConnectMethod()`, `fts3OpenMethod()`, `fts3CursorSeek()`, `fts3SelectLeaf()`, varint helpers, and position-list helpers.

The write path integrates with the FTS shadow schema created by table construction code outside this chunk. SQL templates in `fts3SqlStmt()` assume exact shadow table names (`%_content`, `%_segments`, `%_segdir`, `%_docsize`, `%_stat`) and exact column layouts. `fts3RenameMethod()` mirrors those names when the virtual table is renamed.

`sqlite3Fts3Init()` is the public initialization point for built-in or loadable FTS3. It registers `fts4aux` before registering `fts3`/`fts4`, installs the built-in `simple`, `porter`, and optional ICU tokenizers, optionally registers parser/tokenizer test functions under `SQLITE_TEST`, and shares one tokenizer hash between `fts3` and `fts4`.

The snippet/matchinfo opening connects the query evaluator to later auxiliary-function code. `sqlite3Fts3ExprLoadDoclist()`, `sqlite3Fts3ExprLoadFtDoclist()`, `sqlite3Fts3FindPositions()`, and `fts3ExprIterate()` are used by snippet, offsets, and matchinfo code to load phrase doclists, trim NEAR groups, and find positions for the current row/column.

Shared-cache locking is addressed through `sqlite3Fts3ReadLock()`, which intentionally reads `%_content` before segment tables so concurrent writers see expected lock behavior. This is important because FTS3 failures during commit can roll back a whole transaction.

## Risks And Edge Cases

The code trusts compressed doclist invariants in many hot paths. Some segment-reader paths return `SQLITE_CORRUPT` for malformed node prefix/suffix lengths or doclist terminators, but in-memory pending lists and merge helpers rely on internal generation correctness and asserts. Corrupt shadow-table blobs can still exercise pointer-heavy varint loops.

`fts3DoclistMerge()` requires the caller to provide a sufficiently large output buffer. Most call sites allocate `nLeft+nRight+1`, but in-place AND/NOT merging writes into the left buffer. Future changes that alter output-size assumptions would risk overwrite or truncated results.

Deferred-token optimization intentionally allows `xFilter()` to return a superset. Correctness then depends on `fts3NextMethod()` always calling `fts3EvalDeferred()` before accepting rows and on `sqlite3Fts3CacheDeferredDoclists()` reproducing tokenizer behavior exactly for the content row.

The tokenizer API stores and returns raw C pointers as SQL blobs through `fts3_tokenizer()` and the hidden FTS cursor column. This is a legacy extension mechanism and is process-local, ABI-sensitive, and unsafe to persist or expose across trust boundaries.

`sqlite3Fts3InitTokenizer()` mutates a copy of the tokenizer specification in place while dequoting tokens. It assumes `sqlite3Fts3NextToken()` finds at least one token; malformed or empty tokenizer strings need coverage because `z[n] = '\0'` follows immediately.

The porter tokenizer is ASCII-centric. Non-ASCII bytes are token characters but not case-folded or stemmed in the same way as ASCII words, and custom simple-tokenizer delimiters reject UTF-8 delimiter bytes. Index compatibility depends on using the same tokenizer configuration at query and insert time.

Segment merge and optimize operations can be expensive and write many shadow-table rows. `sqlite3Fts3Optimize()` wraps the merge in a savepoint and rolls back on error, but the special insert path `INSERT INTO tbl(tbl) VALUES('optimize')` maps `SQLITE_DONE` to success and clears pending terms only on non-DONE merge results.

`fts3SpecialInsert()` has a likely typo in the test-only `maxpending=` branch: it checks `nVal>11` but calls `sqlite3_strnicmp(zVal, "maxpending=", 9)` and reads `&zVal[11]`. Test-only tuning commands should verify the intended prefix length.

`fts3SegmentMerge()` asserts `pWriter` after streaming terms. If a segment cursor exists but all terms are empty/ignored, an assert build could fail; non-assert builds would call `fts3SegWriterFlush()` with NULL if not otherwise prevented by cursor behavior.

Several cleanup paths depend on closing reusable resources. Virtual-table methods that indirectly call `sqlite3Fts3ReadBlock()` must close `p->pSegments` before returning to user code, or they may hold blob locks longer than intended.

## Test Signals

Expression parser tests should cover legacy and parenthesized modes, implicit AND, OR precedence differences, explicit AND/NOT, legacy `-token`, `NEAR` and `NEAR/N`, invalid NEAR operands, mismatched parentheses, column qualifiers, quoted phrases, prefix `*`, malformed quotes, and tokenizer errors. Under `SQLITE_TEST`, `fts3_exprtest()` provides a direct parse-tree signal.

Query tests should exercise term, prefix, phrase, OR, AND, NOT, and NEAR searches across multiple columns and multiple segment levels, including cases that require position lists, column filters, doclist stripping, and segment/pending-term merging. They should compare results before and after pending-term flushes and segment optimization.

Deferred-evaluation tests should create high-frequency terms that trigger deferral, then verify `xFilter()` superset behavior is refined correctly by `xNext()` for phrase and boolean queries, including snippets/matchinfo after deferred doclists are cached.

Write-path tests should cover insert, update with same docid, update with changed docid, delete, deleting the last row, rowid/docid conflict handling, pending flush on out-of-order docid, pending flush on size threshold, `%_docsize` and `%_stat` maintenance, and rollback clearing pending terms.

Segment tests should force multi-leaf segments with small test node sizes, level overflow at `FTS3_MERGE_COUNT`, optimize-all merges, inline-root segments, prefix-compressed separator terms, corrupted segment node blobs, and `sqlite3Fts3SegReaderCost()` with and without `%_stat`.

Auxiliary-function tests should validate `snippet()`, `offsets()`, `matchinfo()` argument validation and cursor seeking, plus `optimize()` text/error results. `fts4aux` tests should verify exact, range, and full scans; `ORDER BY term ASC` planning; `*` aggregate rows; per-column document and occurrence counts; and stop-term behavior.

Tokenizer tests should check simple-tokenizer delimiter configuration, ASCII case folding, non-ASCII token inclusion, porter stemming rules, long-word fallback/truncation, digit handling, tokenizer lookup/registration through `fts3_tokenizer()`, and the `SQLITE_TEST` tokenizer test helpers when available.

### subset-b-008420: lines 105143-110689

# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 105143-110689

## Scope And Purpose

This chunk covers four adjacent areas of the FoundationDB vendored SQLite amalgamation:

- the tail of FTS3 `fts3_snippet.c`, including NEAR doclist trimming, `snippet()`, `offsets()`, and `matchinfo()`;
- the R-tree virtual table module implementation, including node persistence tables, query planning/filtering, insert/delete, split/reinsert, and module registration;
- the ICU extension and ICU-backed FTS3 tokenizer;
- a FoundationDB-added `tryReadEveryDbPage()` diagnostic/integrity helper that scans every database page through the pager read path.

The code is mostly optional feature code behind `SQLITE_ENABLE_FTS3`, `SQLITE_ENABLE_RTREE`, and `SQLITE_ENABLE_ICU`, except the final page-scanning helper, which is exported in the local `sqlite3.h` and reaches into SQLite pager/btree internals.

## Important APIs, Types, And Functions

FTS3 snippet and matchinfo code centers on `Fts3Cursor`, `Fts3Table`, `Fts3Expr`, `Fts3Phrase`, `SnippetIter`, `SnippetPhrase`, `SnippetFragment`, `MatchInfo`, `LcsIterator`, `TermOffset`, and `TermOffsetCtx`. Important functions include `fts3ExprNearTrim()`, `fts3ExprLoadDoclists()`, `fts3BestSnippet()`, `fts3SnippetText()`, `sqlite3Fts3Snippet()`, `sqlite3Fts3Offsets()`, `fts3MatchinfoValues()`, `fts3GetMatchinfo()`, and `sqlite3Fts3Matchinfo()`.

The FTS3 helpers use `sqlite3Fts3ExprLoadDoclist()`, `sqlite3Fts3ExprLoadFtDoclist()`, `sqlite3Fts3FindPositions()`, `sqlite3Fts3GetVarint()`, `fts3GetDeltaPosition()`, `sqlite3Fts3SelectDoctotal()`, `sqlite3Fts3SelectDocsize()`, tokenizer module callbacks, SQLite scalar result APIs, and `sqlite3Fts3SegmentsClose()`.

The R-tree module defines `Rtree`, `RtreeCursor`, `RtreeNode`, `RtreeCell`, `RtreeConstraint`, `RtreeMatchArg`, `RtreeGeomCallback`, and `RtreeCoord`. Its virtual table entry points are wired through `rtreeModule`: `rtreeCreate`, `rtreeConnect`, `rtreeBestIndex`, `rtreeDisconnect`, `rtreeDestroy`, `rtreeOpen`, `rtreeClose`, `rtreeFilter`, `rtreeNext`, `rtreeEof`, `rtreeColumn`, `rtreeRowid`, `rtreeUpdate`, and `rtreeRename`. Public registration APIs include `sqlite3RtreeInit()` and `sqlite3_rtree_geometry_callback()`.

R-tree internal helpers include serialization functions `readInt16()`, `readCoord()`, `readInt64()`, `writeInt16()`, `writeCoord()`, `writeInt64()`, node cache/refcount helpers `nodeAcquire()`, `nodeWrite()`, `nodeRelease()`, `nodeHashLookup()`, `nodeHashInsert()`, `nodeHashDelete()`, scan helpers `testRtreeCell()`, `testRtreeEntry()`, `descendToCell()`, and write-path helpers `ChooseLeaf()`, `AdjustTree()`, `SplitNode()`, `Reinsert()`, `rtreeInsertCell()`, `deleteCell()`, `removeNode()`, `fixLeafParent()`, and `fixBoundingBox()`.

The ICU extension registers SQL functions through `sqlite3IcuInit()`: `regexp`, `lower`, `upper`, `like`, and `icu_load_collation`. It uses ICU APIs such as `uregex_open()`, `uregex_setText()`, `uregex_matches()`, `u_strToUpper()`, `u_strToLower()`, `ucol_open()`, `ucol_strcoll()`, and UTF iteration/folding macros. The FTS3 ICU tokenizer exports `sqlite3Fts3IcuTokenizerModule()` and implements tokenizer callbacks `icuCreate()`, `icuDestroy()`, `icuOpen()`, `icuClose()`, and `icuNext()` around ICU `UBreakIterator`.

The local page scan API is `tryReadEveryDbPage(sqlite3 *db, Pgno start, Pgno *pBadPage, int *pBadPageType, int *pBadPageZero)`. It depends on `sqlite3BtreePager()`, `sqlite3BtreeLastPage()`, internal `readDbPage()`, pointer-map macros `PTRMAP_PAGENO`/`PTRMAP_PTROFFSET`, `PENDING_BYTE`, `PGHDR_ZERO_COPY`, and `unpinZeroCopy()`.

## Control Flow

`fts3ExprNearTrim()` starts with a phrase node whose doclist has just been loaded and walks leftward through parent NEAR operators while the phrase is the right child. For each adjacent phrase group it finds the left phrase and calls `sqlite3Fts3ExprNearTrim()` so loaded doclists are pruned to NEAR-compatible positions.

`fts3ExprLoadDoclists()` iterates matchable phrase nodes with `fts3ExprIterate()`, skips NOT-right-hand subtrees, increments phrase/token counts, lazily loads phrase doclists, marks expressions loaded, and then applies NEAR trimming. Snippet, offsets, LCS, and hits calculations share this loader to ensure doclists are available before reading encoded position lists.

Snippet selection first builds a per-phrase `SnippetIter` for one column. `fts3BestSnippet()` scans candidate token windows, scores each candidate with a large bonus for phrases not yet covered by earlier fragments, and records the best fragment. `sqlite3Fts3Snippet()` tries one through four fragments, optionally across all columns, until the covered phrase bitmask equals the seen phrase bitmask or the fragment limit is reached. `fts3SnippetText()` then re-tokenizes the actual column text, may shift the window forward with `fts3SnippetShift()`, appends ellipses, and wraps highlighted tokens with caller-provided markers.

`sqlite3Fts3Offsets()` loads doclists, allocates one `TermOffset` iterator per query token, initializes those iterators for each column, tokenizes the stored column text, and appends `column term start length` tuples for matched terms. It treats tokenizer exhaustion before expected positions as corruption and returns an SQLite error through the scalar function context.

`sqlite3Fts3Matchinfo()` validates the requested format string or uses the default, returns an empty blob for expression-less cursors, and delegates to `fts3GetMatchinfo()`. `fts3GetMatchinfo()` caches the matchinfo array and format string on the cursor, computes phrase count and output size, and populates global fields once per query while recomputing row-local fields only when `isMatchinfoNeeded` is set. `fts3MatchinfoValues()` handles each format character: phrase/column/document counts, average lengths from `%_stat`, row lengths from `%_docsize`, LCS by synchronized position-list iterators, and hits through global and local callbacks.

R-tree scans are planned by `rtreeBestIndex()`. A rowid equality constraint uses strategy 1; coordinate constraints and MATCH geometry constraints use strategy 2 with a compact two-byte-per-constraint `idxStr`. `rtreeFilter()` configures the cursor from this strategy, deserializes geometry blobs when needed, acquires the root node for scans, and descends to the first leaf cell satisfying all constraints. `rtreeNext()` continues depth-first traversal, ascending via parent pointers when a node is exhausted.

R-tree writes run through `rtreeUpdate()`. Deletes locate the leaf through `%_rowid`, remove the cell, condense underfull nodes, shrink the root when it has a single child, and reinsert removed node contents. Inserts validate min/max coordinate ordering, choose or allocate a rowid, select a leaf using `ChooseLeaf()`, then call `rtreeInsertCell()`. Overflow either splits the node or, for the configured R*-tree variant, performs one reinsertion before splitting. Split assignment defaults to `splitNodeStartree()`, which sorts cells by dimension, evaluates margin/overlap/area, and writes left/right nodes and mapping tables.

ICU SQL functions are ordinary scalar functions. `icuLikeFunc()` validates pattern length and optional single-character escape, then runs a recursive Unicode-aware LIKE matcher. `icuRegexpFunc()` caches compiled ICU regex objects with SQLite auxdata keyed to the pattern argument. `icuCaseFunc16()` converts input through ICU upper/lower routines and returns UTF-16 text. `icuLoadCollation()` opens a `UCollator` for a locale and registers it as a SQLite UTF-16 collation.

The ICU tokenizer allocates a cursor containing a folded UTF-16 copy of UTF-8 input plus offset mapping back to byte positions. `icuOpen()` builds that representation and opens a word break iterator. `icuNext()` skips whitespace-like break ranges, converts the current token back to UTF-8 into a reusable buffer, and returns token bytes, byte offsets, and monotonically increasing token position.

`tryReadEveryDbPage()` obtains the main database btree and pager, calculates the last page and the page containing SQLite's pending byte, then loops from `start` through the last page, skipping the pending-byte page. For each page it constructs a stack `PgHdr`, points it at a malloc buffer, and calls `readDbPage()` without inserting the page into the normal page cache. On the first non-OK return it records `*pBadPage` and stops. For `SQLITE_CORRUPT`, it also checks whether the read buffer is all zeroes and tries to read the relevant pointer-map page to report the expected bad page type.

## State And Persistence Behavior

FTS3 state is mostly cursor-local. Doclists become cached on `Fts3Expr` nodes, `isLoaded` prevents duplicate loads, NEAR trimming mutates loaded doclists, `Fts3Cursor.aMatchinfo`/`zMatchinfo` cache the current matchinfo format and array, and snippet/offset string builders own transient SQLite-allocated buffers returned as SQL results. `sqlite3Fts3SegmentsClose()` is called after snippet, offsets, and matchinfo calculations to close FTS segment readers.

R-tree state is persisted in three ordinary SQLite tables: `%_node`, `%_rowid`, and `%_parent`. Node blobs contain depth/cell counts and serialized rowid-or-child plus coordinate cells. `Rtree` keeps prepared statements for these tables and a small in-memory hash of live `RtreeNode` objects. Dirty nodes are written by `nodeWrite()` when their reference count drops to zero; newly allocated nodes receive rowids from `%_node` insertions. Parent and rowid mapping tables are updated separately during insert, split, delete, condense, and reinsert operations.

R-tree schema lifecycle is handled by virtual table callbacks. `rtreeSqlInit()` creates backing tables for `xCreate` and prepares all read/write/delete statements for both create and connect. `rtreeDestroy()` drops all three backing tables. `rtreeRename()` renames all backing tables to match the virtual table name. `rtreeRelease()` finalizes prepared statements and frees the virtual table object once no cursor/update path holds it busy.

ICU extension state consists of registered SQLite functions/collations and per-call/per-pattern allocations. Regex objects are cached through auxdata and closed by `icuRegexpDelete()`. ICU collators are owned by SQLite collation destructors. The FTS3 ICU tokenizer stores locale on the tokenizer object, and each tokenizer cursor owns its break iterator, UTF-16 copy, offset array, and UTF-8 output buffer.

`tryReadEveryDbPage()` is read-oriented and does not intentionally mutate database contents. It does allocate one page-sized heap buffer and may receive zero-copy page memory from `readDbPage()` when the pager is read-only and using WAL; in that case it calls `unpinZeroCopy()` for both the tested page and optional pointer-map page. It reports corruption details through output parameters but does not persist diagnostics.

## Dependencies And Integration Points

The FTS3 functions integrate with SQLite's virtual table/scalar-function path and depend on FTS3 expression parsing, segment/doclist loading, deferred token handling, tokenizer modules, `%_stat`, and `%_docsize`. They are called by SQL auxiliary functions exposed by FTS3 tables and rely on the current row statement (`pCsr->pStmt`) to retrieve original column text.

The R-tree module integrates with SQLite's virtual table API, query planner (`sqlite3_index_info`), scalar function registration, ordinary SQL backing tables, prepared statement APIs, and extension loading. Geometry callbacks bridge user C callbacks into SQL by returning an opaque blob with a magic value, callback pointer, context, and double parameters; MATCH constraints later deserialize that blob for scan filtering.

The ICU extension integrates with SQLite function/collation registration and the external ICU library. Its compile-time availability depends on `SQLITE_ENABLE_ICU`, while the ICU tokenizer also depends on `SQLITE_ENABLE_FTS3`. The tokenizer module pointer returned by `sqlite3Fts3IcuTokenizerModule()` is consumed by FTS3 tokenizer registration code elsewhere in the amalgamation.

The page scan helper is a local integration point between FoundationDB's SQLite API surface and SQLite pager internals. The public prototype appears in the vendored `sqlite3.h`, but the implementation directly creates `PgHdr` objects and uses internal pager/btree state, pointer map calculations, and the local zero-copy VFS extension hooks.

## Risks And Edge Cases

The FTS3 code relies on compact delta/varint encoded position-list formats. Incorrect pointer advancement can corrupt matchinfo, snippets, or offsets. The bitmask approach for snippets uses `u64`, so phrase/token positions beyond the mask width are inherently risky. Deferred tokens require fallback doclist loading for global hits; phrases composed entirely of deferred tokens substitute document-count values because full index stats are unavailable.

`fts3SnippetShift()` opens a tokenizer on a substring and assumes tokenizer positions can be used to determine how far a snippet may shift. Tokenizer errors propagate, but subtle tokenizer offset differences can change displayed snippets without affecting match results.

`sqlite3Fts3Offsets()` returns `SQLITE_CORRUPT` if the stored document text token stream cannot satisfy positions advertised by the index. That is a useful integrity signal but can also surface from tokenizer incompatibility after table creation.

R-tree node integrity checks are partial. `nodeAcquire()` validates root depth and node cell count, but many invariants depend on consistent `%_node`, `%_rowid`, and `%_parent` rows. Parent-chain repair guards against loops, and missing parent data becomes `SQLITE_CORRUPT`. Any bug in split/reinsert/mapping updates can leave durable backing tables inconsistent.

R-tree coordinate handling is sensitive to type mode. `rtree` stores coordinates as 32-bit floats; `rtree_i32` stores 32-bit integers. Inserts reject min greater than max but do not otherwise normalize values. Floating-point equality constraints and area/overlap comparisons can be precision-sensitive.

`deserializeGeometry()` checks blob shape and magic before installing a MATCH callback, but the blob contains callback pointers and context produced by a registered SQL function. This is safe only inside the same process/address space and is not a portable persisted representation.

ICU `icuCaseFunc16()` allocates `nInput * 2 + 2` bytes and calls ICU conversion once. If ICU reports a capacity issue for unusual expansions, this code reports an ICU error instead of retrying with the required size. The error path also does not free `zOutput` before returning, so failures here risk a leak. `icuLikeCompare()` is recursive for `%` matching; the pattern length guard limits but does not eliminate worst-case matching cost.

The ICU tokenizer's offset mapping is delicate because it case-folds UTF-8 into UTF-16 and then maps token boundaries back to byte offsets. Invalid or unusual UTF-8 and multi-code-unit folding can stress the `U8_NEXT`/`U16_APPEND` path and token offset correctness.

`tryReadEveryDbPage()` has several sharp edges: it assumes `db->aDb[0].pBt` is initialized and notes a TODO for clients that have not opened/read the database; it uses `malloc()` without checking for `NULL`; it dereferences output pointers without validation; and it calls `readDbPage()` without explicitly acquiring locks in this function, relying on caller/database state to satisfy pager preconditions. On corruption it reuses the page buffer for pointer-map reads, so the all-zero check must happen before that reuse, as it currently does.

## Test Signals

Relevant FTS3 tests should exercise `snippet()`, `offsets()`, and `matchinfo()` over phrase, multi-token phrase, NEAR, NOT, deferred-token, NULL-column, multi-column, and tokenizer edge cases. Integrity-oriented tests should verify that index/document-tokenizer mismatch produces corruption from `offsets()` and that cached matchinfo is invalidated when format strings change.

R-tree signals include virtual table create/connect/drop/rename, rowid lookup strategy, coordinate range scans, MATCH geometry callbacks, insert/update/delete, duplicate rowid rejection, min/max coordinate constraints, node split and root growth, underfull-node condense and root shrink, and persistence across reconnect. Corruption tests should cover malformed node blobs, missing parent or rowid mappings, parent loops, and invalid root depth.

ICU tests should cover Unicode case folding in `LIKE`, single-character ESCAPE validation, regex cache reuse and invalid patterns, locale-specific upper/lower behavior, loading and using ICU collations, and FTS3 ICU tokenizer token boundaries and byte offsets for multi-byte text.

The local page scan helper can be tested by opening a database through the FoundationDB SQLite build, calling `tryReadEveryDbPage()` from page 1 and non-1 starts, verifying that the pending-byte page is skipped, injecting or simulating read/corruption errors, checking `pBadPage`, `pBadPageType`, and `pBadPageZero`, and running under a VFS path that exercises `xReadZeroCopy`/`xReleaseZeroCopy` to confirm no pinned pages leak.
