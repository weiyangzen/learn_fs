# sources/storage-engines/sqlite/ext/fts5/fts5_test_tok.c

## Purpose

`fts5_test_tok.c` is a test-only virtual table module named `fts5tokenize`. It exposes the output of any registered FTS5 tokenizer as rows so tests can assert token text, byte offsets, and token positions. The virtual table schema is `input HIDDEN, token, start, end, position`, and queries are expected to constrain `input = <string>`.

## Important APIs, types, and functions

`Fts5tokTable` stores the selected tokenizer API and tokenizer instance. `Fts5tokCursor` stores the input string and an in-memory array of `Fts5tokRow` results. `fts5tokDequote()` and `fts5tokDequoteArray()` copy and dequote module arguments from `CREATE VIRTUAL TABLE`. `fts5tokConnectMethod()` declares the schema, locates the tokenizer through `fts5_api.xFindTokenizer`, and creates the tokenizer instance. `fts5tokBestIndexMethod()` accepts only usable equality constraints on the hidden `input` column.

Runtime callbacks are `fts5tokOpenMethod()`, `fts5tokResetCursor()`, `fts5tokCloseMethod()`, `fts5tokFilterMethod()`, `fts5tokCb()`, `fts5tokNextMethod()`, `fts5tokEofMethod()`, `fts5tokColumnMethod()`, and `fts5tokRowidMethod()`. `sqlite3Fts5TestRegisterTok()` registers the module with `sqlite3_create_module`.

## Control flow

Creation/connect dequotes tokenizer arguments, resolves the tokenizer module, and creates a tokenizer instance. `xBestIndex` marks `input = ?` as required and cheap; without it the module leaves a high-cost unusable plan. `xFilter` clears previous cursor rows, copies the input text, invokes the tokenizer once, and collects every emitted token in `fts5tokCb()`. The callback grows the row array geometrically, copies token text, records start/end byte offsets, and advances the position counter only for non-colocated tokens. Cursor iteration then simply walks the precomputed row array.

## State and persistence behavior

The module has no persistent database representation. The tokenizer instance is table-scoped and freed by disconnect/destroy. Token rows are cursor-scoped heap allocations freed on reset/close. Rowids are 1-based positions in the output array rather than source token positions; the `position` column stores tokenizer position semantics including colocated-token handling.

## Dependencies and integration points

This file is built only when both `SQLITE_TEST` and `SQLITE_ENABLE_FTS5` are defined. It depends on `fts5.h`, SQLite virtual table APIs, and an `fts5_api` pointer supplied as module client data by `sqlite3Fts5TestRegisterTok()`. It is registered from the Tcl harness in `fts5_tcl.c`.

## Risks and edge cases

The module materializes all tokens before returning the first row, so very large input strings can allocate large row arrays. It copies token text into nul-terminated strings even though token bytes are length-delimited by the tokenizer, which is acceptable for tests but can obscure embedded nul behavior. `xFilter` returns `SQLITE_ERROR` if the hidden input equality constraint is not provided. Argument dequoting is simple and designed for SQLite module arguments, not general SQL parsing.

## Test signals

This module is a focused tokenizer probe. It verifies tokenizer selection, argument parsing, byte offsets, end offsets, colocated-token position behavior, and compatibility of FTS5 tokenizers with virtual table scan planning. It complements the Tcl tokenizer wrappers by exposing tokenizer output through SQL rows.
