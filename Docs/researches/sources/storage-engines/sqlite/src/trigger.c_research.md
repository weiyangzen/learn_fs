# sources/storage-engines/sqlite/src/trigger.c

## Purpose

`trigger.c` implements SQLite trigger lifecycle and execution. It builds `Trigger` and `TriggerStep` objects during parsing, installs and removes triggers from schema hashes, finds triggers that apply to DML operations, expands and executes `RETURNING` clauses through a trigger-like path, compiles row-trigger subprograms, emits `OP_Program` calls, and computes old/new column usage masks. The file is omitted when `SQLITE_OMIT_TRIGGER` is defined.

## Important APIs, Types, And Functions

- `sqlite3DeleteTriggerStep()` and `sqlite3DeleteTrigger()` free trigger structures and owned expressions/selects/lists.
- `sqlite3TriggerList()` merges table-attached triggers with applicable TEMP triggers and statement-local RETURNING triggers.
- `sqlite3BeginTrigger()` validates CREATE TRIGGER syntax/target/schema/authorization and stores a partially built trigger in `pParse->pNewTrigger`.
- `sqlite3FinishTrigger()` fixes database references, writes `sqlite_schema` rows for normal CREATE TRIGGER statements, and links triggers during schema initialization.
- `sqlite3TriggerSelectStep()`, `sqlite3TriggerInsertStep()`, `sqlite3TriggerUpdateStep()`, and `sqlite3TriggerDeleteStep()` create trigger body steps.
- `sqlite3DropTrigger()`, `sqlite3DropTriggerPtr()`, and `sqlite3UnlinkAndDeleteTrigger()` remove triggers from persistent schema and in-memory hashes.
- `sqlite3TriggersExist()` determines whether DML needs BEFORE/AFTER trigger handling and returns a trigger list plus timing mask.
- RETURNING helpers include `sqlite3ExpandReturning()`, `sqlite3ProcessReturningSubqueries()`, and `codeReturningTrigger()`.
- `codeTriggerProgram()`, `codeRowTrigger()`, `getRowTrigger()`, `sqlite3CodeRowTriggerDirect()`, and `sqlite3CodeRowTrigger()` compile and invoke trigger VDBE subprograms.
- `sqlite3TriggerColmask()` computes old/new column masks needed by triggers.

## Control Flow

CREATE TRIGGER parsing starts in `sqlite3BeginTrigger()`. It resolves the trigger schema, handles TEMP trigger naming, optionally ignores legacy qualified target names during schema reparse, looks up the target table/view, rejects virtual tables and protected shadow/system tables, checks duplicate trigger names and authorization, validates BEFORE/AFTER/INSTEAD OF rules, translates INSTEAD OF to internal BEFORE-on-view representation, and allocates a `Trigger`.

After body parsing, `sqlite3FinishTrigger()` attaches the step list, fixes all schema references, rejects writes to read-only shadow tables from trigger bodies, writes a `sqlite_schema` row and parse-schema op for normal CREATE statements, or during schema initialization inserts the trigger into `trigHash` and links same-schema table triggers into `Table.pTrigger`.

Trigger body step constructors duplicate or retain parse subtrees depending on rename mode. INSERT steps hold target, column list, SELECT, conflict policy, and UPSERT. UPDATE steps duplicate SET/WHERE and fold UPDATE-FROM into an appended nested source term. DELETE steps hold target and WHERE. SELECT steps discard results at execution.

For DML, `sqlite3TriggersExist()` fast-paths tables with no table/TEMP triggers or disabled triggers, then `triggersReallyExist()` filters by operation, UPDATE column overlap, trigger enablement, TEMP trigger policy, and RETURNING behavior. `sqlite3CodeRowTrigger()` iterates the trigger list for a specific timing and operation. Normal triggers call `sqlite3CodeRowTriggerDirect()`, which gets or compiles a cached `TriggerPrg` and emits `OP_Program`. RETURNING triggers are generated inline by `codeReturningTrigger()`.

`codeRowTrigger()` creates a sub-`Parse`, resolves the WHEN expression, emits a jump to the final halt when WHEN is false or null, compiles each trigger step through normal `sqlite3Update()`, `sqlite3Insert()`, `sqlite3DeleteFrom()`, or `sqlite3Select()` calls, captures the VDBE op array as a `SubProgram`, records old/new column masks, transfers parse errors, and caches the program on the top-level parse.

## State And Persistence Behavior

Persistent trigger definitions are stored in `sqlite_schema` as rows of type `trigger`. In-memory trigger state lives in schema `trigHash` tables and, for same-schema table triggers, in `Table.pTrigger` lists. Dropping a trigger deletes the schema row, changes the schema cookie, emits `OP_DropTrigger`, and unlinks/frees in-memory structures during schema change processing.

Execution-time trigger programs are cached per top-level parse in `Parse.pTriggerPrg` and linked into the parent VDBE as `SubProgram` objects. RETURNING uses a statement-local `Returning` object and ephemeral cursor/register state to collect result records. Column masks in `TriggerPrg.aColmask[]` influence how much old/new row data DML callers must load.

## Dependencies And Integration Points

The file depends on parser structures, schema hashes, authorization, DB fixer utilities, name resolution, expression/list/select duplication and deletion, DML code generators, VDBE subprogram APIs, ALTER TABLE rename support, virtual table context rules, shadow table protections, recursive-trigger configuration, RETURNING support, and foreign-key action infrastructure that also uses trigger subprogram mechanics.

It integrates directly with `insert.c`, `update.c`, `delete.c`, `select.c`, `resolve.c`, `build.c`, `alter.c`, `vdbe.c`, schema initialization, and DB config flags such as `SQLITE_EnableTrigger` and `SQLITE_RecTriggers`.

## Risks And Edge Cases

- Schema selection for TEMP triggers, attached databases, orphan TEMP triggers, and legacy qualified target names is compatibility-sensitive.
- Trigger lists are temporarily rewired through `pNext` when TEMP triggers are prepended, so callers must treat returned lists as transient.
- Recursive trigger control depends on `OP_Program` P5 and `SQLITE_RecTriggers`; mistakes can allow infinite recursion or block legal recursion.
- RETURNING is implemented through trigger-like objects but has different timing and inline code generation, especially for virtual tables and UPSERT update paths.
- UPDATE OF column filtering uses name overlap only; renamed columns and duplicated expression lists must stay consistent.
- Trigger subprogram caching is keyed by trigger pointer and conflict policy; schema changes or parse reuse must not retain stale programs.
- Error transfer from sub-parse to outer parse must avoid leaks and preserve the first meaningful error.
- Shadow table/system table restrictions protect internal structures and depend on compile-time options and `sqlite3ReadOnlyShadowTables()`.

## Test Signals

Tests should cover CREATE/DROP trigger schema rows, TEMP triggers on main tables, attached schema names, IF NOT EXISTS, orphan TEMP trigger handling, authorization failures, view/table BEFORE/AFTER/INSTEAD OF validation, virtual/shadow/system table rejection, INSERT/UPDATE/DELETE/SELECT trigger steps, UPDATE OF filtering, UPDATE-FROM in triggers, WHEN clauses, conflict-policy inheritance, recursive trigger enablement, old/new column references and colmasks, RETURNING expansion including `*`, RETURNING subqueries and UPSERT, trigger program cache reuse by conflict policy, schema reparse, ALTER TABLE rename mode, and cleanup on OOM or parse errors.
