# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/TesterFts5.java

## Purpose
`TesterFts5` is the FTS5-specific regression suite loaded by `Tester1` when SQLite is compiled with `ENABLE_FTS5`.

## Important APIs, Types, and Functions
It defines helper `sqlite3_exec()`, `do_execsql_test()`, and `create_test_functions()`, then tests `Fts5ExtensionApi`, `fts5_api`, `fts5_extension_function`, and FTS5 context/iterator callbacks. Registered auxiliary functions include `fts5_rowid`, `fts5_columncount`, `fts5_columnsize`, `fts5_columntext`, `fts5_columntotalsize`, `fts5_aux1/2`, `fts5_inst`, `fts5_pinst`, `fts5_pcolinst`, `fts5_rowcount`, `fts5_phrasesize`, `fts5_phrasehits`, and `fts5_tokenize`.

## Control Flow
The constructor calls synchronized `runTests()`, which executes `test1()` through `test6()`. Each test opens an in-memory DB, creates FTS5 tables, registers Java auxiliary functions through `fts5_api.getInstanceForDb(db)`, runs SQL queries, compares `Arrays.toString()` results, and closes the DB.

## State and Persistence Behavior
State is mostly local to test functions. `test1()` checks singleton API objects and verifies an auxiliary function's `xDestroy()` runs on database close. Auxdata tests verify values persist per function instance and can be cleared.

## Dependencies and Integration Points
It imports `CApi`, `Tester1` helpers, C API handle types, output pointers, and FTS5 bridge classes.

## Risks
Tests depend on FTS5 compile support and exact SQLite result/error wording for some range failures. String concatenation in callbacks is simple but not performance-oriented.

## Test Signals
Expected query result strings validate rowid extremes, column sizes/text/totals, auxdata behavior, instance and phrase iteration, row counts, phrase size, query-phrase callbacks, tokenizer output, singleton identity, and destroy callbacks.
