# sources/storage-engines/sqlite/ext/fts3/fts3_tokenize_vtab.c

## Purpose

Implements the `fts3tokenize` virtual table, a diagnostic table-valued interface that tokenizes an input string with a selected FTS3 tokenizer and returns one row per token.

## Important APIs, types, and functions

`Fts3tokTable` stores the tokenizer module and tokenizer instance. `Fts3tokCursor` stores copied input text, tokenizer cursor, current rowid, token text, byte offsets, and token position. Important helpers are `fts3tokQueryTokenizer()` and `fts3tokDequoteArray()`. Virtual-table callbacks include connect/create, disconnect/destroy, best-index, open, reset/close, filter, next, eof, column, and rowid. `sqlite3Fts3InitTok()` registers module name `fts3tokenize`.

## Control flow

Connect declares schema `input, token, start, end, position`, dequotes tokenizer arguments, resolves the tokenizer in the shared hash, and creates a tokenizer instance. Best-index strongly prefers an equality constraint on `input`. Filter copies the bound input into nul-terminated memory, opens a tokenizer cursor, and immediately advances to the first token. Next calls tokenizer `xNext()` and resets cursor state on `SQLITE_DONE`.

## State and persistence

The virtual table has no persistent backing storage. Table state owns one tokenizer instance for the vtab lifetime. Cursor state owns input copies and tokenizer cursors for each scan.

## Dependencies and integration points

Depends on `Fts3Hash` tokenizer registry, `sqlite3Fts3Dequote()`, tokenizer modules, and SQLite virtual-table APIs. It is registered from FTS initialization and shares tokenizer implementations with real FTS tables.

## Risks and test signals

Risks include forgetting the required `input = ?` constraint, tokenizer lifetime leaks, dequoting argument mismatches with `CREATE VIRTUAL TABLE`, and incorrect byte offsets for tokenizers with Unicode behavior. Test signals are `SELECT * FROM fts3tokenize(...) WHERE input=?` rows, default `simple` tokenizer behavior, tokenizer-argument quoting, unknown tokenizer errors, EOF/reset behavior, and planner use of the equality constraint.
