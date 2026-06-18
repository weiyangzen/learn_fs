# sources/test-tools/syzkaller/pkg/coveragedb/functions.go

Purpose: maps file/line pairs to function names using the `functions` Spanner table generated during coverage merging.

Important APIs/types/functions: `FuncLines`, `MakeFuncFinder`, `FunctionFinder`, `addLine`, and `FileLineToFuncName`.

Control flow: `MakeFuncFinder` queries function records for namespace/date/duration, iterates rows into `FuncLines`, and records each line in a nested map keyed by file path then line number. `FileLineToFuncName` returns the mapped function or an explicit missing-file/missing-line error.

State and persistence: reads Spanner; stores the lookup in memory. No writes.

Dependencies and integration: depends on `spannerclient`, Spanner SQL, `TimePeriod`, and `covermerger` output of `FuncLines`. Used by UI/report paths that need function names for line-level coverage.

Risks: later rows overwrite earlier function names for the same file/line. There is no namespace cache or partial loading. Query reads all functions for a period, which may be heavy.

Test signals: no direct tests in this subset. It is indirectly tied to `covermerger` function-line output and database save tests.
