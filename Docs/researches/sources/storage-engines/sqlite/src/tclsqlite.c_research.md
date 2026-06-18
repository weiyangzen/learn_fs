# Research: sources/storage-engines/sqlite/src/tclsqlite.c

## Purpose

`tclsqlite.c` implements SQLite's Tcl extension and optional standalone
`tclsh`-style executable. It exposes a top-level `sqlite3` Tcl command that
opens an SQLite connection and creates a Tcl command for that connection. The
connection command then provides methods for SQL evaluation, statement cache
control, callbacks/hooks, backup/restore, serialization, incremental BLOB
channels, user-defined SQL functions/collations, transactions, tracing, and
test-oriented features.

The file is designed to build both appended to the SQLite amalgamation and as a
separate source file. It embeds a copy of `tclsqlite.h` near the top so the
amalgamated Tcl source has the same Tcl include and Tcl 8.6/9.0 compatibility
logic.

## Important Types And State

- `SqlFunc` records Tcl-backed SQL scalar functions: interpreter, script object,
  owning database, safe-eval flag, requested return type, name, and linked-list
  pointer.
- `SqlCollate` records Tcl-backed collations: interpreter, script text, and
  linked-list pointer.
- `SqlPreparedStmt` wraps a cached `sqlite3_stmt`, SQL text identity, LRU links,
  and Tcl object references for parameters bound with `SQLITE_STATIC`.
- `SqliteDb` is the central per-connection state and deliberately stores
  `sqlite3 *db` first. It owns the Tcl interpreter, callback script strings,
  hook Tcl objects, user function/collation lists, prepared statement cache,
  open incremental blob channel list, recent statement statistics, nested
  transaction count, URI open flags, reference count, and test-only legacy
  prepare mode.
- `IncrblobChannel` wraps `sqlite3_blob` as a Tcl channel with current seek
  offset, close flags, associated `SqliteDb`, and connection-local linked-list
  links.
- `DbEvalContext` is the state machine for `$db eval`: SQL text, current
  prepared statement, target array/dict variable, cached column names, and eval
  flags.

## Top-Level Open Flow

`Sqlite3_Init()` initializes Tcl stubs, creates the `sqlite3` command and,
unless `SQLITE_3_SUFFIX_ONLY` is defined, a legacy `sqlite` alias, then provides
the Tcl package. Safe interpreter init and unload entry points return
`TCL_ERROR` because SQLite uses filesystem and persistent state.

The `sqlite3` command is implemented by `DbMain()`. With `-version`,
`-sourceid`, or `-has-codec`, it returns metadata. Otherwise it parses handle
name, filename, and options including `-vfs`, `-readonly`, `-create`,
`-nofollow`, `-nomutex`, `-fullmutex`, `-uri`, and `-translatefilename`. The
default open mode is read-write/create with `SQLITE_OPEN_NOMUTEX`, unless
`SQLITE_TCL_DEFAULT_FULLMUTEX` selects full mutexes for test builds.

`DbMain()` optionally translates the Tcl filename, opens with
`sqlite3_open_v2()`, converts open failures into Tcl errors, initializes a
`SqliteDb` with a default 10-statement cache, and creates the connection Tcl
command. On Tcl versions with non-recursive evaluation support, it registers an
NRE adaptor so `$db eval` and `$db transaction` can avoid deep Tcl recursion.

## Connection Command Surface

`DbObjCmd()` dispatches connection methods using `Tcl_GetIndexFromObj()`. Major
method groups are:

- SQL execution: `eval`, `exists`, `onecolumn`, and `format`.
- Transaction control: `transaction`, with `deferred`, `immediate`, or
  `exclusive` top-level begin style and savepoint-based nesting.
- Statement cache: `cache flush` and `cache size n`, capped by
  `MAX_PREPARED_STMTS`.
- Binding behavior: automatic Tcl variable binding for `$`, `:`, and `@`
  parameters plus `bind_fallback`.
- Hooks and callbacks: `busy`, `progress`, `authorizer`, `commit_hook`,
  `rollback_hook`, `wal_hook`, `update_hook`, `preupdate hook`,
  `collation_needed`, `trace`, `trace_v2`, `profile`, and `unlock_notify`.
- User extensions: `function` and `collate`.
- File and memory movement: `backup`, `restore`, `serialize`, `deserialize`,
  and the legacy `copy` importer.
- Connection metadata/actions: `changes`, `total_changes`,
  `last_insert_rowid`, `errorcode`, `erroroffset`, `interrupt`, `complete`,
  `config`, `enable_load_extension`, `timeout`, `status`, `version`,
  `nullvalue`, and `close`.
- Incremental BLOB I/O: `incrblob`, returning a Tcl channel name.

Many methods are conditionally compiled and return explicit Tcl errors when
the required SQLite feature was omitted.

## Statement Preparation, Binding, And Evaluation

`dbPrepare()` selects `sqlite3_prepare_v3()` and uses
`SQLITE_PREPARE_PERSISTENT` when the statement cache is large enough to make
lookaside preservation more valuable. In `SQLITE_TEST` builds it can use legacy
`sqlite3_prepare()` for compatibility tests.

`dbPrepareAndBind()` trims leading whitespace, looks for a cached prepared
statement whose SQL prefix matches the next statement, unlinks cache hits from
the LRU list, or prepares and allocates a new `SqlPreparedStmt`. It then binds
host parameters named with `$`, `:`, or `@` from Tcl variables. Missing
variables either bind NULL or invoke `zBindFallback`. Binding preserves Tcl
object lifetimes for blobs and text passed with `SQLITE_STATIC` by incrementing
object refcounts and storing them in `apParm`; `dbReleaseStmt()` later decrefs
them.

Binding type decisions inspect Tcl object internal type names. Bytearrays with
no string representation, and all `@name` parameters, bind as BLOBs. Boolean,
integer, wide integer, and double Tcl objects bind as the corresponding SQLite
numeric types. Other values bind as UTF-8 text. Missing values bind NULL.

`DbEvalContext` drives multi-statement SQL execution. `dbEvalStep()` prepares
the next statement as needed, steps it until a row or completion, records
statement status counters on reset, handles schema retry only for legacy
prepare test mode, and releases statements back to the cache or discards them
on error. `dbEvalRowInfo()` lazily builds column-name Tcl objects and populates
the target array/dict `*` entry. `dbEvalColumnValue()` converts SQLite column
types back into Tcl objects, using `pDb->zNull` for SQL NULL.

`$db eval SQL` without a script returns a flat Tcl list of all column values.
With a script, `DbEvalNextCmd()` fills either same-named variables, an array, or
a dict for each row, supports `-withoutnulls` and `-asdict`, evaluates the
script for each row, and treats `break` as normal completion.

## Transactions And Persistence Behavior

`$db transaction` always opens either a top-level transaction or a savepoint
named `_tcl_transaction`. Nested calls use savepoints. `DbTransPostCmd()`
chooses `COMMIT`, `ROLLBACK`, `RELEASE`, or `ROLLBACK TO ...; RELEASE` based on
the script result and nesting depth. It temporarily disables the authorizer
while running transaction-control SQL so Tcl authorizer scripts do not block the
wrapper's cleanup. If commit fails, it reports the SQLite error and attempts a
rollback.

The extension itself persists only through the underlying SQLite database and
through Tcl-visible channels/commands. Connection state is memory-resident:
prepared statement cache, callback scripts, hook objects, functions,
collations, and incremental blob channels are all freed when the connection Tcl
command is deleted and `SqliteDb.nRef` reaches zero.

`backup` and `restore` use the SQLite backup API in 100-page steps. `restore`
retries a few `SQLITE_BUSY` steps with sleep. `serialize` returns a Tcl
bytearray from `sqlite3_serialize()`, preferring `SQLITE_SERIALIZE_NOCOPY` but
copying when required. `deserialize` copies the Tcl bytearray into SQLite
malloc memory and passes ownership with `SQLITE_DESERIALIZE_FREEONCLOSE`, using
readonly or resizable flags according to options.

The legacy `copy` importer reads a Tcl channel line by line, splits on a
separator, inserts inside a transaction, maps empty or null-indicator fields to
SQL NULL, and rolls back on shape or SQLite errors.

## Callback And Hook Control Flow

The busy, progress, commit, trace, profile, trace_v2, WAL, update, preupdate,
rollback, unlock-notify, authorizer, collation, and SQL function callbacks all
bridge SQLite C callbacks into Tcl script evaluation.

Callbacks append structured arguments to the configured Tcl script. Examples:
the authorizer appends action name and four context strings; update hooks append
operation, database, table, and rowid; WAL hook appends database name and frame
count and expects an integer SQLite return code; trace_v2 appends statement or
connection pointers and event-specific data. Most callbacks reset the Tcl
result after fire-and-forget use; errors in rollback/WAL hooks are reported via
`Tcl_BackgroundError()`.

`tclSqlFunc()` evaluates a Tcl script as an SQL scalar function. It converts
SQLite arguments to Tcl values, evaluates the script efficiently using a
shallow list copy, treats `TCL_BREAK` as SQL NULL, reports Tcl errors via
`sqlite3_result_error()`, and maps the Tcl result back to SQLite using either a
declared `-returntype` or internal Tcl object type inference.

`tclSqlCollate()` evaluates a Tcl script with the two strings to compare and
returns the integer Tcl result as the SQLite collation comparison value.

## Incremental Blob Channels

When incremental BLOB support is enabled, `$db incrblob ?-readonly? ?DB? TABLE
COLUMN ROWID` opens a `sqlite3_blob` and wraps it in a Tcl channel. The channel
type implements close, read, write, seek, wide seek, watch no-op, and handle
failure. Reads clamp to the blob size and advance `iSeek`. Writes reject
attempts past the fixed blob size and return Tcl channel errors on SQLite I/O
failures.

Open channels are linked from `SqliteDb.pIncrblob`. `closeIncrblobChannels()`
unregisters them during connection destruction, and the channel close path
removes the node from the linked list, closes the `sqlite3_blob`, and frees the
channel wrapper.

## Dependencies And Integration Points

This file depends on Tcl C APIs, SQLite public APIs, and, when not amalgamated,
`sqlite3.h`, C runtime headers, and platform process headers. Optional
integration includes QRF (`qrf.h`) for `$db format`, unlock notify, preupdate
hook, deserialize/serialize, load extension, incremental blob, tracing,
progress callbacks, authorization, and standalone `TCLSH`.

It is a major integration point for SQLite's Tcl test suite. Test-only code
supports legacy prepare selection, unlock-notify global test variables,
last-statement pointer inspection, and debug-break behavior in standalone
shell mode.

## Risks

This file has several risk clusters:

- Tcl script callbacks can re-enter SQLite or delete the connection command.
  The reference-counting around `SqliteDb` and eval contexts is therefore
  critical.
- Statement caching with `SQLITE_STATIC` bindings depends on accurately
  retaining Tcl object references until `sqlite3_reset()` and release.
- The transaction wrapper can be confused by user scripts that manually issue
  transaction-control SQL inside `$db transaction`; the code comments call out
  this tricky scenario.
- Type inference based on Tcl internal type names is version-sensitive and must
  be kept compatible with Tcl 8.6 and Tcl 9.0.
- The legacy `copy` parser is separator-based rather than CSV-aware and
  materializes/modifies line buffers in place.
- Conditional compilation creates many build surfaces; missing-feature paths
  need tests so Tcl users get deterministic errors rather than unresolved
  symbols.

## Test Signals

High-value tests include opening with every option combination, failing opens,
SQL variable binding for all Tcl value types, `bind_fallback` success/error,
statement cache LRU behavior, eval list/array/dict modes, `-withoutnulls`,
nested transaction commit/rollback/savepoint behavior, callback registration
and clearing, user-defined function return-type mapping, collation callbacks,
authorizer decisions, busy/progress interruption, trace_v2 masks, backup and
restore error paths, serialize/deserialize readonly and max-size options,
incremental blob read/write/seek/close behavior, connection deletion during
callbacks, Tcl 8.6 vs Tcl 9.0 builds, and omitted-feature builds.
