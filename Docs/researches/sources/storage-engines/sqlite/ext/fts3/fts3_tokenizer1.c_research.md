# sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer1.c

## Purpose

Implements the built-in `simple` tokenizer. It splits text on ASCII delimiters, lowercases ASCII uppercase letters, and leaves non-delimiter bytes otherwise unchanged.

## Important APIs, types, and functions

`simple_tokenizer` stores the base tokenizer and a 128-byte delimiter table. `simple_tokenizer_cursor` tracks input pointer, byte length, offset, token index, reusable token buffer, and buffer size. Tokenizer callbacks are `simpleCreate()`, `simpleDestroy()`, `simpleOpen()`, `simpleClose()`, and `simpleNext()`. `sqlite3Fts3SimpleTokenizerModule()` exports the module.

## Control flow

Creation either marks caller-supplied ASCII delimiters from the second tokenizer argument or defaults all non-alphanumeric ASCII bytes to delimiters. Open records the input buffer and length. `simpleNext()` skips delimiters, scans the next non-delimiter byte span, grows its output buffer, ASCII-folds the token into that buffer, and returns byte offsets and increasing token positions.

## State and persistence

Tokenizer delimiter configuration is per tokenizer instance. Cursor token buffers are transient. Persisted index terms depend on delimiter configuration and case folding, so changing tokenizer arguments after indexing requires reindexing.

## Dependencies and integration points

Uses the common tokenizer ABI and SQLite allocation. It is the default tokenizer for many FTS3 paths and is also used by tokenizer tests and `fts3tokenize`.

## Risks and test signals

Risks include lack of UTF-8-aware case folding, unsupported high-bit delimiter arguments, embedded nul or byte-length assumptions, and index incompatibility if delimiter rules change. Test signals are token boundary output, ASCII lowercasing, custom delimiter rejection for UTF-8 bytes, offsets, and default tokenizer behavior when no tokenizer is specified.
