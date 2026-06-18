# sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer.c

## Purpose

Implements generic tokenizer registration, tokenizer-spec parsing, and SQL access to the tokenizer hash via `fts3_tokenizer()`. It is the bridge between FTS table definitions, tokenizer modules, and optional extension/test registration.

## Important APIs, types, and functions

Public/internal entry points include `sqlite3Fts3InitTokenizer()`, `sqlite3Fts3InitHashTable()`, `sqlite3Fts3IsIdChar()`, and `sqlite3Fts3NextToken()`. The scalar function implementation is `fts3TokenizerFunc()`. Test-only helpers include `testFunc()`, `registerTokenizer()`, `queryTokenizer()`, and `intTestFunc()`.

## Control flow

`sqlite3Fts3InitTokenizer()` copies the tokenizer specification string, extracts and dequotes the tokenizer name with `sqlite3Fts3NextToken()`, looks up the module in `Fts3Hash`, parses remaining dequoted arguments, calls module `xCreate()`, and sets the tokenizer's module pointer. `fts3TokenizerFunc()` either looks up a tokenizer pointer by name or stores a supplied pointer blob, subject to `SQLITE_DBCONFIG_ENABLE_FTS3_TOKENIZER` or bound-parameter safety checks. `sqlite3Fts3InitHashTable()` registers one- and two-argument SQL functions and test functions.

## State and persistence

The shared tokenizer hash is in-memory per database/FTS initialization. Created tokenizer instances are heap objects owned by FTS table or caller lifecycle. No persistent state is written, but tokenizer choice affects persisted index terms, so changes require reindexing.

## Dependencies and integration points

Depends on `Fts3Hash`, tokenizer ABI, `sqlite3Fts3Dequote()`, `sqlite3Fts3ErrMsg()`, SQLite scalar-function APIs, and DB config `SQLITE_DBCONFIG_ENABLE_FTS3_TOKENIZER`. The expression parser, indexer, snippet/offset logic, `fts3tokenize`, and tests all call through this setup.

## Risks and test signals

The pointer-returning SQL function is intentionally guarded because exposing raw pointers is unsafe. Other risks include tokenizer-spec parsing around quoted identifiers, argument allocation failures, unknown tokenizer errors, and module `xCreate()` returning success without a tokenizer. Test signals are tokenizer registration/query tests, disabled `fts3_tokenizer()` behavior, bound-parameter exceptions, tokenizer test output, and internal README example validation.
