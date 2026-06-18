# sources/storage-engines/sqlite/src/func.c

## Purpose

`func.c` implements and registers many SQLite built-in SQL scalar, aggregate, and window-capable functions. It covers core string/blob/numeric functions, LIKE/GLOB matching and planner metadata, aggregate state machines for sum/count/min/max/group_concat, optional math and percentile families, optional load-extension and diagnostics functions, and registration glue that populates the global `sqlite3BuiltinFunctions` hash during initialization.

Date/time, JSON, window-specific functions, and ALTER TABLE functions are registered from other modules but are coordinated by `sqlite3RegisterBuiltinFunctions()`.

## Important APIs, Types, And Functions

Externally visible internal functions are `sqlite3_strglob()`, `sqlite3_strlike()`, `sqlite3QuoteValue()`, `sqlite3RegisterPerConnectionBuiltinFunctions()`, `sqlite3RegisterLikeFunctions()`, `sqlite3IsLikeFunction()`, and `sqlite3RegisterBuiltinFunctions()`.

Scalar implementations include `minmaxFunc`, `typeofFunc`, `subtypeFunc`, `lengthFunc`, `bytelengthFunc`, `absFunc`, `instrFunc`, `printfFunc`, `substrFunc`, `roundFunc`, `upperFunc`, `lowerFunc`, `randomFunc`, `randomBlob`, `last_insert_rowid`, `changes`, `total_changes`, `nullifFunc`, `versionFunc`, `sourceidFunc`, `errlogFunc`, compile-option functions, `unistrFunc`, `quoteFunc`, `unicodeFunc`, `charFunc`, `hexFunc`, `unhexFunc`, `zeroblobFunc`, `replaceFunc`, `trimFunc`, `concatFunc`, `concatwsFunc`, optional `soundexFunc`, optional `loadExt`, optional math functions, and debug functions such as `filestatFunc`, `fpdecodeFunc`, and `parseuriFunc`.

Pattern matching is centered on `struct compareInfo`, `patternCompare()`, `likeFunc()`, `sqlite3_strlike()`, and `sqlite3_strglob()`. Aggregate/window state types include `SumCtx`, `CountCtx`, `GroupConcatCtx`, and optional `Percentile`.

Registration uses the `FUNCTION`, `VFUNCTION`, `DFUNCTION`, `SFUNCTION`, `LIKEFUNC`, `WAGGREGATE`, `MFUNCTION`, and `INLINE_FUNC` macros to describe function name, arity, encoding, user data, callbacks, and flags.

## Control Flow

Scalar functions receive `sqlite3_context`, argument count, and `sqlite3_value **`, then return using `sqlite3_result_*()` APIs. Most functions explicitly preserve NULL behavior by returning without setting a result. Allocation helpers such as `contextMalloc()` enforce `SQLITE_LIMIT_LENGTH` and translate OOM/too-large conditions into context errors.

String functions convert values through SQLite value APIs, which may change encoding or materialize text/blob data. Functions such as `length()`, `substr()`, `instr()`, `trim()`, `unistr()`, `char()`, and LIKE/GLOB explicitly walk UTF-8. Blob paths usually operate on byte counts.

`patternCompare()` recursively evaluates LIKE/GLOB wildcard semantics with optimizations for ASCII stop characters and a pattern length limit enforced by `likeFunc()`. `sqlite3IsLikeFunction()` exposes wildcard and case-sensitivity metadata to the query planner so LIKE range optimizations can be considered only for compatible built-ins and literal escapes.

Aggregate functions use `sqlite3_aggregate_context()` for per-group or per-window state. `sumStep()` keeps exact integer accumulation until overflow or non-integer input forces Kahan-Babuska-Neumaier floating accumulation. Window inverse callbacks subtract rows for `sum`, `count`, `group_concat`, and optional percentile. `group_concat` appends separators before values for historical compatibility and tracks separator lengths for sliding window removal. Optional percentile accumulates doubles, validates a stable percentile argument, sorts on demand, and keeps sorted order for window usage.

`sqlite3RegisterBuiltinFunctions()` builds a static `FuncDef` array, calls module registration hooks for alter/window/date/json functions, and inserts all built-ins into the global function hash. `sqlite3RegisterPerConnectionBuiltinFunctions()` overloads `MATCH` per connection for virtual-table behavior. `sqlite3RegisterLikeFunctions()` can replace LIKE implementations when case sensitivity changes.

## State And Persistence Behavior

Most state is transient per function invocation, aggregate group, window frame, or database connection. Random functions use SQLite PRNG state. `last_insert_rowid()`, `changes()`, and `total_changes()` read connection state. `sqlite_log()` writes to the configured log callback as a side effect. `load_extension()` can load process code only when the connection has enabled the SQL function. Built-in function definitions live in the process-global `sqlite3BuiltinFunctions` hash after initialization and are read-only afterward except for per-connection overloads and LIKE re-registration.

No database pages are written directly by this file, but function results can be persisted by SQL statements that store them.

## Dependencies And Integration Points

`func.c` depends on `sqliteInt.h`, `vdbeInt.h`, SQLite value/result APIs, collation handling (`OP_CollSeq`, `sqlite3MemCompare()`), memory APIs, UTF-8 helpers, string accumulators, PRNG, compile-option APIs, extension loading, VFS file-control diagnostics, parser URI logic, and libm when `SQLITE_ENABLE_MATH_FUNCTIONS` is enabled. It integrates with the planner through flags such as `SQLITE_FUNC_LIKE`, `SQLITE_FUNC_CASE`, `SQLITE_FUNC_LENGTH`, `SQLITE_FUNC_BYTELEN`, `SQLITE_FUNC_MINMAX`, `SQLITE_FUNC_COUNT`, `SQLITE_FUNC_ANYORDER`, `SQLITE_INNOCUOUS`, and `SQLITE_SELFORDER1`.

Build options significantly alter surface area: `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_ENABLE_MATH_FUNCTIONS`, `SQLITE_ENABLE_PERCENTILE`, `SQLITE_ENABLE_UNKNOWN_SQL_FUNCTION`, `SQLITE_SOUNDEX`, `SQLITE_DEBUG`, and `SQLITE_ENABLE_FILESTAT`.

## Risks

High-risk areas include memory-limit enforcement, UTF-8 boundary walking, text/blob coercion order, overflow handling, aggregate inverse correctness, LIKE/GLOB recursion and pattern complexity, and planner flags that allow transformations only when semantics are exact. `load_extension()` is intentionally security-sensitive. `quote()` and `unistr_quote()` must produce SQL literals without truncation or incorrect escaping except for documented embedded-NUL behavior. Optional percentile holds all non-null numeric values, so memory growth is proportional to input rows. Math and floating functions must handle NULL, domain errors, infinities, and compile-time libm availability consistently.

## Test Signals

Signals include SQL logic tests for every built-in function, NULL propagation, type coercion, UTF-8 multi-byte handling, invalid UTF-8 tolerance where expected, maximum length failures, OOM injection, LIKE/GLOB escape semantics and planner range optimization, case-sensitive LIKE re-registration, aggregate/window inverse equivalence to non-window results, integer overflow in `abs()` and `sum()`, `group_concat` with varying separators in windows, extension-loading authorization, optional math domain behavior, percentile validation and interpolation, and debug-only function availability under the correct build flags.
