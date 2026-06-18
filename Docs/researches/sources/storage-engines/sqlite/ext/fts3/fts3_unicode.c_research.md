# sources/storage-engines/sqlite/ext/fts3/fts3_unicode.c

## Purpose

Implements the built-in `unicode61`-style tokenizer for FTS3/FTS4 when Unicode tokenization is not disabled. It performs UTF-8 decoding, Unicode alphanumeric classification, case folding, optional diacritic removal, and configurable token/separator exceptions.

## Important APIs, types, and functions

`unicode_tokenizer` stores diacritic-removal mode and sorted exception codepoints. `unicode_cursor` stores input bytes, current offset, token index, and reusable UTF-8 output buffer. Key functions are `unicodeCreate()`, `unicodeDestroy()`, `unicodeOpen()`, `unicodeClose()`, `unicodeNext()`, `unicodeAddExceptions()`, `unicodeIsException()`, `unicodeIsAlnum()`, and `sqlite3Fts3UnicodeTokenizer()`.

## Control flow

Creation parses arguments `remove_diacritics=0/1/2`, `tokenchars=...`, and `separators=...`, building a sorted exception list that inverts the generated Unicode alnum classifier. `unicodeNext()` scans to the next token character, then reads token characters and combining diacritics with `READ_UTF8`, folds each codepoint through `sqlite3FtsUnicodeFold()`, optionally drops standalone diacritics, writes UTF-8 with `WRITE_UTF8`, and returns original byte offsets.

## State and persistence

Tokenizer options are per table tokenizer instance. Cursor state and buffers are transient. Persisted FTS index terms depend on Unicode tables, diacritic mode, and exception arguments.

## Dependencies and integration points

Depends on generated helpers in `fts3_unicode2.c`: `sqlite3FtsUnicodeIsalnum()`, `sqlite3FtsUnicodeIsdiacritic()`, and `sqlite3FtsUnicodeFold()`. Uses the tokenizer ABI and SQLite memory routines. It integrates as a tokenizer module for indexing, querying, snippets, offsets, and `fts3tokenize`.

## Risks and test signals

Risks include invalid UTF-8 handling, changes to generated Unicode tables, duplicate exception insertion, ignoring standalone diacritic exceptions, buffer growth failures, and byte-offset correctness for multibyte input. Test signals are Unicode token boundaries, case folding, diacritic modes 0/1/2, tokenchars/separators options, malformed UTF-8, and snippet/offset behavior over multibyte text.
