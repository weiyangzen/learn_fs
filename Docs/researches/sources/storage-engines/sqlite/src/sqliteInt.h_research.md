# Research: sources/storage-engines/sqlite/src/sqliteInt.h

## Scope

This document covers the complete `sources/storage-engines/sqlite/src/sqliteInt.h` header. The file is SQLite's central internal interface header: it establishes platform/compiler configuration, core scalar typedefs and macros, internal object layouts, parse-tree contracts, schema/planner/VDBE state carriers, feature-gated declarations, and the large private prototype surface used across the SQLite core.

Unlike a `.c` implementation file, this header does not implement long algorithms directly. Its operational importance is that many implementation files compile against these definitions, so changes here alter control flow and memory/state semantics throughout the engine.

## Purpose

- Normalize platform, compiler, OS, memory, threading, endian, file-size, mmap, debug, coverage, and feature-omission settings before SQLite's private sources are compiled.
- Define the internal object model for connections, attached databases, schemas, tables, indexes, columns, collations, functions, savepoints, virtual tables, parse contexts, expressions, SELECTs, triggers, CTEs, windows, walkers, and global configuration.
- Define flags and constants that encode SQL semantics, planner behavior, result routing, opcode P5 meanings, conflict resolution, join types, affinity, expression properties, table/index properties, database/schema state, and optimizer disable masks.
- Provide internal APIs that connect parser, resolver, schema loader, DDL/DML code generators, expression code generator, SELECT planner, WHERE planner, btree/pager/VDBE layers, virtual-table subsystem, triggers, foreign keys, WAL/checkpoint code, memory/debug utilities, and test hooks.
- Centralize compatibility constraints between public API bit values, parser token codes, VDBE opcode flags, btree flags, planner flags, and test-suite expectations.

## Important APIs, Types, And Functions

### Build, Platform, And Utility Contracts

- Platform setup includes `msvc.h`, `vxworks.h`, optional `SQLITE_CUSTOM_INCLUDE`, public `sqlite3.h`, optional autoconf `sqlite_cfg.h`, and `sqliteLimit.h`.
- Large-file and platform macros include `_LARGE_FILE`, `_FILE_OFFSET_BITS`, `_LARGEFILE_SOURCE`, `_GNU_SOURCE`, `_BSD_SOURCE`, `_USE_32BIT_TIME_T`, `SQLITE_USE_SEH`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_THREADSAFE`, `SQLITE_POWERSAFE_OVERWRITE`, default memory-status behavior, allocator selection, `_XOPEN_SOURCE`, and debug/coverage macros.
- Compiler and intrinsic helpers include `GCC_VERSION`, `MSVC_VERSION`, `SQLITE_ATOMIC_INTRINSICS`, `AtomicLoad`, `AtomicStore`, `SQLITE_NOINLINE`, `SQLITE_INLINE`, `deliberate_fall_through`, byte-swap intrinsics, and `SQLITE_HAVE_C99_MATH_FUNCS`.
- Core numeric and pointer contracts include `i64`, `u64`, `u32`, `u16`, `i16`, `u8`, `i8`, `bft`, `tRowcnt`, `LogEst`, `uptr`, `Bitmask`, `VList`, pointer-size/endian macros, `SQLITE_WITHIN`, `SQLITE_OVERFLOW`, `ROUND8`, `ROUND8P`, `EIGHT_BYTE_ALIGNMENT`, `TWO_BYTE_ALIGNMENT`, `LARGEST_INT64`, `SMALLEST_INT64`, `SQLITE_MAX_U32`, `LOGEST_MIN`, and `LOGEST_MAX`.
- Debug/test macros include `testcase`, `TESTONLY`, `VVA_ONLY`, `ALWAYS`, `NEVER`, `OK_IF_ALWAYS_TRUE`, `OK_IF_ALWAYS_FALSE`, `ONLY_IF_REALLOC_STRESS`, `OSTRACE`, `WHERETRACE`, `TREETRACE`, `CORRUPT_DB`, `SQLITE_*_BKPT`, `IOTRACE`, memory-type assertions, and parser trace/coverage declarations.
- General helpers include `ArraySize`, `IsPowerOfTwo`, `SWAP`, `MIN`, `MAX`, `UNUSED_PARAMETER`, `UNUSED_PARAMETER2`, `SQLITE_SKIP_UTF8`, ASCII/EBCDIC character-class macros, varint fast-path macros, and boolean/integer conversion declarations.

### Core Connection, Schema, And Storage Types

- `struct sqlite3` is the per-connection root object. It owns VFS selection, VDBE list, collation/function registries, attached database array, transaction/change counters, open-state, limits, parser pointer, trace/update/commit/rollback/WAL hooks, lookaside configuration, busy handler, default static `Db` slots, savepoints, virtual-table transaction lists, client data, unlock-notify state, deferred constraint counters, and many feature-gated callback fields.
- `struct Db` maps a schema name to a `Btree`, synchronous safety level, and `Schema`.
- `struct Schema` stores schema-cookie/generation data plus hash tables for tables, indexes, triggers, and foreign keys; file format, encoding, schema flags, cache size, and autoincrement sequence table.
- `DbHasProperty`, `DbSetProperty`, and related macros manipulate schema flags such as `DB_SchemaLoaded`, `DB_UnresetViews`, and `DB_ResetWanted`.
- `struct Table`, `Column`, `Index`, `IndexSample`, `FKey`, `KeyInfo`, and `UnpackedRecord` encode in-memory schema and index comparison contracts used by DDL, DML, query planning, constraint checking, btree cursor comparison, and VDBE record handling.
- Table/index flags include `TF_*`, `COLFLAG_*`, `SQLITE_IDXTYPE_*`, `XN_ROWID`, `XN_EXPR`, `KEYINFO_ORDER_*`, `HasRowid`, `VisibleRowid`, `IsView`, `IsVirtual`, `IsHiddenColumn`, and conflict-resolution constants `OE_*`.
- `struct Savepoint`, `AutoincInfo`, and foreign-key declarations tie parser/codegen state to transaction and constraint behavior.

### Functions, Collations, Virtual Tables, And Extensions

- `struct FuncDef`, `FuncDestructor`, `FuncDefHash`, and macros such as `FUNCTION`, `VFUNCTION`, `SFUNCTION`, `MFUNCTION`, `JFUNCTION`, `INLINE_FUNC`, `TEST_FUNC`, `DFUNCTION`, `PURE_DATE`, `LIKEFUNC`, `WAGGREGATE`, and `INTERNAL_FUNCTION` define built-in and connection-local SQL function descriptors.
- Function flags such as `SQLITE_FUNC_CONSTANT`, `SQLITE_FUNC_SLOCHNG`, `SQLITE_FUNC_NEEDCOLL`, `SQLITE_FUNC_MINMAX`, `SQLITE_FUNC_ANYORDER`, `SQLITE_FUNC_DIRECT`, `SQLITE_FUNC_UNSAFE`, `SQLITE_FUNC_INLINE`, `SQLITE_FUNC_BUILTIN`, `SQLITE_FUNC_INTERNAL`, and subtype flags are central to resolver, code generator, schema-safety, and optimizer behavior.
- `struct CollSeq` defines collation names, encodings, comparison callbacks, user payloads, and destructors.
- `struct Module` and `struct VTable` define per-module and per-connection virtual-table state, including module reference counts, eponymous tables, per-connection `sqlite3_vtab` handles, risk levels, savepoint depth, and delayed disconnect behavior.
- Virtual-table declarations include module creation, connect/create/destroy, transaction hooks, eponymous-table setup, shadow-table checks, function overloads, all-schema use, and no-op replacements when virtual tables are omitted.

### Parser, AST, SELECT, Trigger, CTE, And Window Types

- `struct Parse` is the main parser/code-generator context. It carries the connection, VDBE under construction, errors, lookaside state, write/cookie masks, cursor/register allocation counters, temporary register caches, parser mode, nested parse boundaries, trigger context, shared-cache locks, autoincrement info, cleanup actions, current DDL objects, variable list, WITH clause, ALTER rename state, and feature-gated virtual-table state.
- `PARSE_HDR_SZ`, `PARSE_RECURSE_SZ`, `PARSE_TAIL_SZ`, `PARSE_MODE_*`, `IN_DECLARE_VTAB`, `IN_RENAME_OBJECT`, and `IN_SPECIAL_PARSE` describe how `Parse` is reset or interpreted during recursive parsing and special DDL modes.
- `Token`, `Expr`, `ExprList`, `IdList`, `SrcItem`, `SrcList`, `OnOrUsing`, `NameContext`, `Select`, `SelectDest`, `AggInfo`, `IndexedExpr`, `Subquery`, `Upsert`, `Trigger`, `TriggerStep`, `TriggerPrg`, `Returning`, `With`, `Cte`, `CteUse`, `Window`, `Walker`, and `DbFixer` define the AST, name-resolution, SELECT-routing, trigger, RETURNING, window, and tree-walk contracts.
- Expression flags, list flags, source flags, join flags, name-context flags, SELECT flags, and result destinations are defined with explicit cross-constraints. Important groups include `EP_*`, `ENAME_*`, `JT_*`, `WHERE_*`, `NC_*`, `SF_*`, `SRT_*`, `M10d_*`, and walker return codes `WRC_Continue`, `WRC_Prune`, `WRC_Abort`.
- `yDbMask` abstracts attached-database bitmasks for small and large `SQLITE_MAX_ATTACHED` configurations.

### Global Configuration And Memory State

- `struct Lookaside` and `LookasideSlot` define per-connection lookaside allocation pools, including two-size lookaside support, disable counters, statistics, free/init lists, memory bounds, and the `DisableLookaside`/`EnableLookaside` macros.
- `struct Sqlite3Config` stores process-global configuration and initialization state: memory, mutex, page-cache methods, heap/page buffers, lookaside defaults, mmap defaults, shared-cache setting, sorter settings, init mutex, logging hooks, SQL log hook, VDBE coverage hook, memdb limit, test callback, localtime fault injection, PRNG seed, rowid-in-view control, and debug tune slots.
- `SQLITE_WSD`, `GLOBAL`, and `sqlite3GlobalConfig` adapt static global state for platforms without writable static data.
- Allocation and diagnostics declarations cover malloc initialization, db-aware allocation, page allocation, stack allocation, memory subsystem choices, memdebug typing, status counters, lookaside accounting, benign malloc hooks, OOM reporting, and fault simulation.

### Internal Prototype Surface

The prototype block exposes the private APIs implemented across the SQLite core:

- Parser and DDL: `sqlite3RunParser`, `sqlite3FinishCoding`, `sqlite3StartTable`, `sqlite3AddColumn`, `sqlite3AddPrimaryKey`, `sqlite3AddCheckConstraint`, `sqlite3EndTable`, `sqlite3CreateIndex`, `sqlite3DropTable`, `sqlite3DropIndex`, `sqlite3Alter*`, `sqlite3NestedParse`, `sqlite3ReadSchema`, `sqlite3Init*`, and object lookup helpers.
- Expression and SELECT: expression allocation/deletion/duplication, expression-list/source-list helpers, name resolution, collation/affinity helpers, scalar expression codegen, boolean branch codegen, aggregate analysis, SELECT construction/deletion/codegen, subquery handling, CTE/window functions, vector helpers, and constant/nullability/implication checks.
- DML and constraints: `sqlite3Insert`, `sqlite3Update`, `sqlite3DeleteFrom`, row/index delete generation, constraint checks, insertion completion, foreign-key actions/checks, generated columns, autoincrement, triggers, RETURNING, UPSERT, and change counting.
- Planner and VDBE integration: `sqlite3WhereBegin`, `sqlite3WhereEnd`, one-pass decisions, ordering/distinct checks, min/max early-out, register allocation, VDBE acquisition, schema verification, transaction/savepoint codegen, key-info allocation, record/varint helpers, rowset/bitvec utilities, and opcode property exports.
- Runtime subsystems: WAL/checkpoint, journal/memjournal, backup restart/update, virtual tables, loadable extensions, attach/detach, URI parsing, memory DB, compile-option diagnostics, thread workers, DBPAGE/DBSTAT virtual tables, UNIX KVVFS, hardware timer, and statement scan status.

## Control Flow

`sqliteInt.h` first sets preprocessor state in a strict order. Platform-specific setup precedes `sqlite3.h` so large-file, MinGW time, MSVC warning, and public API configuration take effect before system/public declarations are consumed. It then imports limit, hash, parser, OS, pager, btree, VDBE, pcache, and mutex headers after defining the small integer and forward-declared private types they require.

Feature switches shape compiled control flow globally. `SQLITE_OMIT_*`, `SQLITE_ENABLE_*`, `SQLITE_THREADSAFE`, memory subsystem macros, mmap defaults, endian detection, floating-point omission, virtual-table omission, CTE/window/upsert/foreign-key/trigger omission, WAL omission, and test/debug settings either provide real declarations or replace calls with no-op macros. This means implementation files can call internal APIs unconditionally while the header erases code paths for omitted features.

Connection-level control flow is organized around `sqlite3`. Open connections move through `SQLITE_STATE_*` values; active VDBEs, transaction counters, savepoint lists, callback pointers, virtual-table transaction lists, and attached `Db` entries guide prepare/step/commit/rollback/close behavior. `sqlite3.flags`, `sqlite3.mDbFlags`, and `dbOptFlags` drive pragma-selected behavior, internal schema-change state, and test-control optimizer disabling.

Schema flow starts from `sqlite3Init*` and schema parsing. `InitData` communicates `OP_ParseSchema` rows into `sqlite3InitCallback`, populating `Schema` hash tables with `Table`, `Index`, `Trigger`, and `FKey` objects. DDL code uses `Parse.pNewTable`, `pNewIndex`, `pNewTrigger`, schema cookies, root pages, ALTER flags, and rename-token state to build or rewrite schema entries. Runtime schema invalidation flows through reset/expire declarations and schema flags.

SQL compilation flows through `Parse`. The parser builds `Expr`, `ExprList`, `SrcList`, `Select`, `TriggerStep`, `Upsert`, `With`, and `Window` objects. Name resolution uses `NameContext` chains and `Walker` callbacks to bind identifiers, mark aggregates/windows/subqueries, resolve upsert and RETURNING scopes, and set flags consumed later by code generation and optimization. `Parse` cursor/register counters and masks then drive VDBE bytecode generation.

SELECT and expression control flow is encoded by shared AST flags. `Select.selFlags`, `Expr.flags`, `SrcItem.fg`, `NameContext.ncFlags`, `WHERE_*`, and `SRT_*` select transformations such as flattening, coroutine/materialized subqueries, DISTINCT/order routing, aggregate handling, RIGHT JOIN support, one-pass DML, fixed LIMIT use, and result destinations. The header also documents union-field access rules in compact structs such as `Expr` and `SrcItem`; implementation code must branch on the associated flags before reading union members.

Planner and execution flow bridge through declared APIs. WHERE planning receives `SrcList`, WHERE expressions, grouping/order lists, `Select`, and control flags, then returns `WhereInfo` consumed by DML/SELECT codegen. Expression codegen emits VDBE opcodes using table/index metadata, collation/affinity contracts, function descriptors, `KeyInfo`, `UnpackedRecord`, and VDBE register/cursor allocation. DML code invokes constraint, foreign-key, trigger, index-key, generated-column, and insertion/deletion helpers declared here.

Debug/test control flow is woven in by macros. `testcase()`, coverage counters, `ALWAYS`/`NEVER`, corruption and misuse breakpoints, `TREETRACE`, `WHERETRACE`, `IOTRACE`, memdebug typing, VDBE coverage hooks, parser trace/coverage, fault injectors, and tuning slots allow test builds to exercise and observe branches that disappear or become no-ops in production builds.

## State And Persistence Behavior

This header does not directly mutate persistent database pages, but it defines almost all structures and flags through which persistent effects are staged.

Persistent database state is represented in memory by `Db`, `Schema`, `Table`, `Column`, `Index`, `FKey`, `Trigger`, and `CollSeq`. Root page numbers, schema cookies, file-format and encoding fields, table/index hash entries, foreign-key hash entries, AUTOINCREMENT sequence table references, column default/generated expressions, triggers, and partial/index expressions mirror or derive from `sqlite_schema` and btree content.

Connection state in `sqlite3` controls transaction durability and visibility. `autoCommit`, `nVdbeActive`, `nVdbeRead`, `nVdbeWrite`, `nVdbeExec`, savepoint lists, deferred-constraint counters, WAL callbacks, busy handlers, mmap size, open flags, error state, change counters, query-only/defensive/trusted-schema flags, and attached `Db` slots all affect how later implementation code reads or writes database files.

Parser state in `Parse` is transient but persistence-sensitive. `writeMask`, `cookieMask`, `checkSchema`, `isMultiWrite`, `mayAbort`, `disableTriggers`, `pAinc`, `pTriggerPrg`, `pCleanup`, `pNewTable`, `pNewIndex`, `pNewTrigger`, `pWith`, `pRename`, `nTab`, and `nMem` determine the VDBE program that will eventually perform durable btree, journal, WAL, schema, and temp-store operations.

Global state in `Sqlite3Config` is process-wide and long-lived. It owns initialization flags, configured allocators/mutexes/pcache, heap/page-cache backing storage, shared-cache default, mmap defaults, logging/test/fault hooks, PRNG seed, localtime substitution, sorter and lookaside defaults, and debug tuning. Under `SQLITE_OMIT_WSD`, the `GLOBAL` indirection changes how this state is stored and accessed.

Memory lifetime contracts are explicit. Schema objects may be shared through btrees; TEMP schema is connection-owned. Virtual-table `VTable` objects are per-connection and can be moved to a delayed disconnect list. `FuncDestructor` uses reference counts. `KeyInfo` uses reference counts. `RCStr` embeds a reference-count header before string data. Lookaside allocations are connection-bound and disabled during some schema parsing. Parser cleanup objects defer deletion until parse teardown.

Temporary state includes expression trees, source lists, select lists, CTE usage objects, window descriptors, walkers, trigger programs, aggregate info, indexed-expression mappings, rowsets, bitvectors, temporary register caches, and ephemeral cursor numbers. These are not durable, but incorrect state here can compile persistent writes with wrong semantics.

## Dependencies And Integration Points

- Public API dependency: the header includes `sqlite3.h` and depends on public constants, callbacks, VFS/file/mutex/pcache/mem APIs, `sqlite3_value`, `sqlite3_context`, `sqlite3_module`, result codes, open flags, text encodings, prepare flags, and destructor types.
- Generated parser dependency: it includes `parse.h` and declares Lemon parser entry points (`sqlite3Parser*`). Many AST opcodes reuse parser token codes, so token/opcode alignment is a semantic dependency.
- Core storage dependencies: `os.h`, `pager.h`, `btree.h`, `vdbe.h`, `pcache.h`, and `mutex.h` are included after private typedef setup. Flags in this header must match pager, btree, and VDBE constants, as documented by multiple assert-enforced value constraints.
- Schema and DDL integration: `build.c`, `prepare.c`, `alter.c`, `pragma.c`, `attach.c`, and schema-loader code rely on the object layouts and declarations for creating, validating, clearing, renaming, and reparsing schema objects.
- Parser/resolver/codegen integration: `parse.y`, `resolve.c`, `expr.c`, `select.c`, `insert.c`, `update.c`, `delete.c`, `trigger.c`, `upsert.c`, `where*.c`, `window.c`, and `cte` code use `Parse`, AST structures, name contexts, walker callbacks, flags, and prototypes defined here.
- VDBE integration: opcode P5 flags, `SelectDest`, expression codegen declarations, `KeyInfo`, `UnpackedRecord`, `FuncDef`, `CollSeq`, register helpers, cursor counters, and VDBE profile/trace declarations connect SQL compilation to bytecode execution.
- Virtual-table and extension integration: module/vtab structures and declarations coordinate `sqlite3_create_module`, eponymous tables, shadow tables, vtab transactions/savepoints, function overloads, JSON/carray virtual tables, and loadable extensions.
- Memory and threading integration: allocator selection, lookaside, memdebug, status counters, mutex methods, atomic load/store, worker-thread declarations, and no-WSD support are shared by all subsystems.
- Test integration: TH3 and internal tests rely on specific flag numeric values noted in comments, coverage macros, fault injectors, parser coverage, VDBE coverage, memdebug tags, debug tree/where tracing, test-only virtual tables, and compile-option diagnostics.

## Risks And Edge Cases

- Numeric flag compatibility is fragile. Many macros are required to match public API constants, parser tokens, btree flags, pager flags, VDBE op flags, `NameContext` flags, `Select` flags, or TH3 expectations. Changing a bit value can silently corrupt semantics across files.
- Struct layout is a cross-file ABI inside SQLite. `Expr`, `Parse`, `SrcItem`, `Table`, `Index`, `sqlite3`, `Sqlite3Config`, and lookaside structs are read and written by many implementation files. Field reordering or union changes can break assumptions about reset ranges, reduced expression sizes, memory allocation sizes, or debug assertions.
- Compact union fields require correct guard flags. `Expr.x`, `Expr.y`, `SrcItem.u1/u2/u3/u4`, `NameContext.uNC`, `Table.u`, `Parse.u1`, and `FuncDef.u` are intentionally overloaded. Missing a flag check can read stale data as another type.
- Feature-gated no-op macros can hide missing tests. Builds with omitted virtual tables, triggers, foreign keys, CTEs, windows, WAL, floating point, UTF-16, subqueries, deserialize, or auth compile different code paths; a change must be validated against both enabled and omitted configurations.
- Memory ownership boundaries are subtle. Schema objects may outlive a connection in shared-cache contexts, while lookaside memory cannot be used for shared schema content. Virtual tables delay disconnect, CTE usage persists via parser cleanup, and function/key/string descriptors use reference counting.
- Threading behavior depends on compile-time and runtime state. `SQLITE_THREADSAFE`, mutex omission/noop builds, atomic intrinsics, interrupt state, unlock-notify fields, global config mutexes, and shared-cache locks must stay coherent.
- Endian, pointer-size, alignment, mmap, large-file, MinGW time, SEH, and VxWorks setup affect portability. Incorrect ordering or defaults can create binary incompatibility, wrong file offsets, invalid pointer casts, or unaligned access assumptions on less common platforms.
- UTF-8 handling explicitly tolerates malformed input but does not promise stable character boundaries for malformed sequences. Code using `SQLITE_SKIP_UTF8` or related helpers must only depend on memory safety and byte preservation where documented.
- Debug and coverage macros deliberately change branch behavior. `ALWAYS`, `NEVER`, mutation testing, realloc-stress, and coverage counters can make unreachable production branches reachable in tests; error-handling code must remain valid under these modes.
- `SQLITE_DYNAMIC` is a sentinel cast to `sqlite3RowSetClear`, not a normal destructor. Code comparing destructor pointers must preserve this special case.
- Global writable-static-data omission changes storage through `sqlite3_wsd_find()`. New global variables need to follow the `SQLITE_WSD`/`GLOBAL` pattern where appropriate.

## Test Signals

- Build-matrix tests should cover default, debug, coverage, mutation/realloc-stress, no-threadsafe, mutex-noop/omit, no-WSD, floating-point omitted, virtual-table omitted, trigger/foreign-key omitted, WAL omitted, UTF-16 omitted, subquery omitted, CTE/window/upsert omitted, STAT4 enabled, memdebug, and mmap-disabled configurations.
- Compile-option tests should confirm defaults for `SQLITE_THREADSAFE`, memory status, file format, recursive triggers, temp store, worker threads, page-cache initial size, sorter-ref size, mmap limits, synchronous defaults, and allocator selection.
- Schema tests should exercise schema load/reset, attached databases, shared-cache schema sharing, TEMP schema lifetime, schema cookie checks, `sqlite_schema`/legacy name aliases, ALTER TABLE reparsing flags, generated columns, hidden columns, strict tables, shadow tables, views, triggers, and foreign-key hash lookups.
- Connection-state tests should cover busy handlers, interrupts, savepoints, deferred constraints, autocommit boundaries, rollback/commit callbacks, update/preupdate hooks, WAL callbacks, trace/profile hooks, client data destructors, error byte offsets, sick/zombie close states, and unlock-notify builds.
- Parser/AST tests should cover expression reduced/token-only nodes, expression depth limits, vector expressions, collations, generated columns, nested SELECTs, CTE materialization hints, recursive CTEs, aggregate/window flags, UPSERT, RETURNING, RIGHT/FULL joins, NATURAL/USING/ON joins, table-valued functions, and `INDEXED BY` metadata.
- Planner and VDBE tests should cover optimizer-disable masks, WHERE one-pass modes, DISTINCT/order result destinations, min/max ORDER BY modes, Bloom filter flags, statement scan status, expression indexes, partial indexes, covering-index bitmasks beyond 63 columns, rowid and WITHOUT ROWID tables, and `KeyInfo` sort/null-order behavior.
- Function/collation tests should verify built-in function initializer macros, direct-only/unsafe/innocuous behavior, deterministic/slow-changing behavior, subtype propagation, collation-needed callbacks, undefined collations in indexes, JSON function flags, LIKE optimization flags, aggregate ordering, and window function registration.
- Memory tests should run OOM/fault injection through schema parse, expression/list growth, lookaside allocation, page allocation, parser cleanup, RCStr reference counting, function destructor reference counting, KeyInfo reference counting, virtual-table delayed disconnect, and no-WSD global access.
- Portability tests should include endian detection, pointer-size casts, alignment macros, large file support, mmap boundary defaults, MinGW 32-bit time handling, MSVC SEH/intrinsics, OpenBSD/QNX mmap disablement, Apple target includes, ASCII/EBCDIC character helpers, and malformed UTF-8 scans.
- Debug/test-signal tests should validate `testcase()` coverage, `SQLITE_*_BKPT` line reporting, `TREETRACE`/`WHERETRACE` guarded builds, parser trace/coverage, VDBE coverage callbacks, I/O tracing, memdebug allocation types, `sqlite3NoTempsInRange`, and TH3-sensitive flag values.
