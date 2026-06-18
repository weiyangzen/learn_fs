# sources/storage-engines/sqlite/src/vdbe.h

## Purpose

`vdbe.h` is the main non-public interface for building and managing SQLite VDBE bytecode programs. It keeps `Vdbe` itself opaque, but exposes the opcode representation, P4 operand ownership rules, trigger subprogram representation, code-generation helpers, bytecode patching helpers, lifecycle entry points, record comparison interfaces, and optional instrumentation hooks used by the parser, code generator, executor, explain, scanstatus, and tests.

The file sits between SQL compilation and VDBE execution. Parser/codegen modules include it to allocate a VM, append opcodes, attach typed P4 payloads, resolve labels, mark database dependencies, finalize a statement into runnable form, and later reset/finalize/delete it. Execution details and concrete runtime state live in `vdbeInt.h` and companion `.c` files.

## Important APIs, Types, and Constants

`typedef struct Vdbe Vdbe` intentionally hides the VM layout from most code. The file forward-declares `Mem`, `SubProgram`, and `SubrtnSig` because opcode payloads refer to those internal structures without exposing their full definitions here.

`SubrtnSig` describes a reusable subroutine used to materialize the right-hand side of an `IN` expression. It records the RHS SELECT id, completion flag, affinity string, generated ephemeral table, entry address, and return-register slot. The reusable-subroutine contract is stateful: codegen can share a coded RHS only after `bComplete` is true and the stored address/table/register fields are valid.

`VdbeOp` is the bytecode instruction format: `opcode`, `p1`, `p2`, `p3`, `p4`, and `p5`. `p2` is commonly a jump destination. `p4` is a tagged union whose meaning is controlled by `p4type`, and may hold integers, strings, functions, collations, `Mem`, virtual tables, `KeyInfo`, integer arrays, subprograms, schema objects, or cursor-hint expressions. Optional fields add explain comments, VDBE coverage source locations, and execution/cycle counters.

`SubProgram` stores trigger or subprogram bytecode, memory/cursor requirements, `OP_Once` state, a recursion token, and a linked-list pointer used to track visited subprograms. `VdbeOpList` is a compact literal opcode form for bulk insertion via `sqlite3VdbeAddOpList()`.

`P4_*` constants define both type and ownership semantics. Values above `P4_FREE_IF_LE` do not own resources. Values at or below it require cleanup by VDBE code. This boundary is a high-risk API contract because changing a `p4type` can silently turn a borrowed pointer into an owned allocation or vice versa.

`COLNAME_*` constants define the layout of `Vdbe.aColName`: result name, declaration type, database, table, and source column. `COLNAME_N` varies with `SQLITE_ENABLE_COLUMN_METADATA` and `SQLITE_OMIT_DECLTYPE`, so code that indexes `aColName` must use the macros rather than hard-coded counts.

`ADDR(X)` maps unresolved labels returned by `sqlite3VdbeMakeLabel()` into `Parse.aLabel[]` indexes. `opcodes.h` is generated from VDBE sources and supplies opcode numbers.

The prototypes cluster into these groups:

- Bytecode allocation/emission: `sqlite3VdbeCreate()`, `sqlite3VdbeAddOp0..4()`, `sqlite3VdbeAddOp4Dup8()`, `sqlite3VdbeAddOp4Int()`, `sqlite3VdbeAddFunctionCall()`, `sqlite3VdbeAddOpList()`, `sqlite3VdbeLoadString()`, `sqlite3VdbeMultiLoad()`, and coroutine helpers.
- Bytecode patching and labels: `sqlite3VdbeChangeOpcode()`, `sqlite3VdbeChangeP1/P2/P3/P5/P4()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeJumpHere()`, `sqlite3VdbeJumpHereOrPopInst()`, `sqlite3VdbeChangeToNoop()`, `sqlite3VdbeDeletePriorOpcode()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeCurrentAddr()`, and `sqlite3VdbeMakeLabel()`.
- Statement lifecycle: `sqlite3VdbeMakeReady()`, `sqlite3VdbeFinalize()`, `sqlite3VdbeReset()`, `sqlite3VdbeResetStepResult()`, `sqlite3VdbeRewind()`, `sqlite3VdbeDelete()`, `sqlite3VdbeRunOnlyOnce()`, `sqlite3VdbeReusable()`, `sqlite3VdbeTakeOpArray()`, and `sqlite3VdbeSwap()`.
- Statement metadata: `sqlite3VdbeSetNumCols()`, `sqlite3VdbeSetColName()`, `sqlite3VdbeSetSql()`, `sqlite3VdbeDb()`, `sqlite3VdbePrepareFlags()`, and optional normalized-SQL double-quote tracking.
- Runtime values and records: `sqlite3VdbeGetBoundValue()`, `sqlite3VdbeSetVarmask()`, `sqlite3MemCompare()`, `sqlite3BlobCompare()`, record unpack/compare functions, `sqlite3VdbeAllocUnpackedRecord()`, `sqlite3VdbeFindCompare()`, and `sqlite3MemSetArrayInt64()`.
- Subprograms and dependencies: `sqlite3VdbeLinkSubProgram()`, `sqlite3VdbeHasSubProgram()`, `sqlite3VdbeUsesBtree()`, `sqlite3VdbeAddParseSchemaOp()`, and `sqlite3VdbeSetP4KeyInfo()`.
- Diagnostics and instrumentation: explain helpers, comments, branch coverage macros, scanstatus registration helpers, opcode printing, cursor-hint validation, and bytecode virtual-table initialization.

## Control Flow

A parser creates a `Vdbe`, emits instructions through `sqlite3VdbeAddOp*()` helpers, uses labels for forward jumps, attaches P4 payloads, annotates explain/coverage/scanstatus metadata, and marks btree dependencies. Once SQL compilation is complete, `sqlite3VdbeMakeReady()` fixes memory/register/cursor requirements and makes the VM runnable. Runtime APIs in `vdbeapi.c` and execution code in `vdbe.c` then step, reset, and finalize the same object through the lifecycle prototypes declared here.

Patching helpers are central to codegen control flow. Many SQL constructs emit placeholder jumps first and call `sqlite3VdbeJumpHere()` or `sqlite3VdbeResolveLabel()` after the destination address is known. `sqlite3VdbeChangeToNoop()` and `sqlite3VdbeDeletePriorOpcode()` support late peephole/codegen corrections.

The instrumentation macros are compile-time no-ops unless their feature flags are enabled. With `SQLITE_VDBE_COVERAGE`, every branch opcode is expected to be tagged so coverage testing can detect untagged or unexercised bytecode branches. With explain comments or scanstatus enabled, extra fields and callbacks tie generated bytecode back to plan output and statement metrics.

## State and Persistence Behavior

This header does not persist data itself. It defines the contracts for in-memory VDBE bytecode and statement metadata. The important stateful contracts are P4 ownership, column-name slot layout, unresolved label encoding, subprogram linkage, saved SQL flags, btree dependency masks, and optional per-op execution counters.

`SQLITE_PREPARE_SAVESQL` is an internal prepare flag that keeps SQL text for automatic reprepare and expanded SQL. `SQLITE_PREPARE_MASK` separates public prepare flags from internal bits. `sqlite3VdbeSetVarmask()` and binding-related support interact with plan invalidation: parameters used in ways that can affect plans are tracked so a later bind can expire the VM.

## Dependencies and Integration Points

`vdbe.h` depends on types from SQLite core headers such as `Parse`, `FuncDef`, `CollSeq`, `VTable`, `KeyInfo`, `Table`, `Index`, `Expr`, `UnpackedRecord`, and `sqlite3_context`. It includes generated `opcodes.h`, so build ordering matters.

The main integration points are parser/codegen modules, `vdbe.c` execution, `vdbeaux.c` lifecycle and bytecode assembly helpers, `vdbemem.c` value handling, `vdbesort.c`, btree/pager dependencies, explain/scanstatus code, bytecode virtual table code, and test-only VDBE coverage plumbing.

## Risks and Edge Cases

The P4 type boundary is the main memory-management risk. Misclassified P4 payloads can leak, double-free, or retain stale pointers. `P4_TABLEREF`, `P4_SUBRTNSIG`, `P4_FUNCCTX`, and other typed pointers require the implementation and cleanup paths to agree exactly.

Conditional compilation changes structure size and behavior. `VdbeOp` gains counters under scanstatus/profile, comments under explain comments, cursor-hint expressions under cursor hints, and source-line coverage under VDBE coverage. Code assuming a stable binary layout across feature sets would be fragile.

Label handling is intentionally encoded with bitwise complement. Passing raw negative labels or resolved addresses to the wrong helper can patch invalid jumps. Column metadata also depends on build options, so indexing `aColName` incorrectly can read the wrong metadata slot.

## Test Signals

Useful tests include SQL statements that produce forward jumps, subroutines, triggers, `IN (SELECT ...)` RHS materialization, explain and explain-query-plan output, scanstatus counters, branch coverage builds with `SQLITE_VDBE_COVERAGE`, normalized SQL builds, and statements whose host-parameter bindings trigger automatic reprepare. Memory tests should stress P4 payload ownership, subprogram deletion, statement finalization, and no-op opcode rewrites.
