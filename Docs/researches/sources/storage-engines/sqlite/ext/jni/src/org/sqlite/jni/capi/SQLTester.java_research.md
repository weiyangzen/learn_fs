# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/SQLTester.java

## Purpose
`SQLTester.java` is an internal SQL-script interpreter and command runner for testing the SQLite JNI bindings against SQLite-style test scripts. It is not a public API; it lives in `org.sqlite.jni.capi` so it can access package-visible JNI helpers and native test extensions.

## Important APIs, Types, and Functions
The file defines `SQLTester`, result formatting enums, test exceptions, `Outer`, `Util`, command classes, `CommandDispatcher`, and `TestScript`. `SQLTester.execSql()` prepares one or more UTF-8 SQL statements with `sqlite3_prepare_v2()`, steps them, formats result rows, and finalizes statements. Commands implement script operations such as `--run`, `--result`, `--glob`, `--tableresult`, `--json`, `--open`, `--new`, `--close`, `--db`, `--null`, `--column-names`, and `--testcase`. Native hooks include `strglob()` and `installCustomExtensions()`.

## Control Flow
`main()` loads custom native extensions, parses CLI flags, registers an auto-extension that applies accumulated initialization SQL, then calls `runTests()`. Each script creates a `TestScript`, which line-scans the file, recognizes directives and command lines, appends non-command SQL to the tester input buffer, and dispatches commands. Result commands consume SQL from the input buffer, call `execSql()`, and compare normalized output to expected literals or globs.

## State and Persistence Behavior
State is process-local: input/result buffers, `dbInitSql`, null display text, current database slot, counters, and up to seven `sqlite3` handles. Database files are opened by script commands; the default `test.db` is deleted before/after runs. `reset()` closes all handles and clears script-scoped state but preserves overall counters.

## Dependencies and Integration Points
The class depends heavily on `CApi`, `OutputPointer`, `sqlite3`, `sqlite3_stmt`, callback proxies, `ResultCode`, and native library `sqlite3-jni`. It integrates with `test-script-interpreter.md` semantics and SQLite auto-extension behavior.

## Risks
The parser is intentionally narrow and rejects or skips incompatible directives, C-preprocessor lines, mixed module names, and some script features. It assumes UTF-8 script input and manually decodes multibyte characters. Statement finalization/reset in error paths is critical because failed `INSERT ... RETURNING` cases can leave locks. The auto-extension plus lazy default DB open can interact with initialization timing.

## Test Signals
Useful signals are successful execution of SQL test scripts, accurate escaped/asis result buffers, glob/table-result matching, unknown command skipping, clean finalization on errors, and no leaked open database handles after `runTests()`.
