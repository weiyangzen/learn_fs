# sources/storage-engines/sqlite/ext/fts3/fts3_icu.c

## Purpose

Implements the optional ICU-backed FTS3 tokenizer, compiled only with `SQLITE_ENABLE_ICU`. It uses ICU word-boundary analysis and Unicode case folding to tokenize multilingual input.

## Important APIs, types, and functions

`IcuTokenizer` stores the base tokenizer and optional locale string. `IcuCursor` stores an ICU `UBreakIterator`, UTF-16 input copy, UTF-8 offset map, output buffer, and token counter. Tokenizer callbacks are `icuCreate()`, `icuDestroy()`, `icuOpen()`, `icuClose()`, and `icuNext()`. `sqlite3Fts3IcuTokenizerModule()` returns the static module.

## Control flow

Creation copies the optional locale. Opening a cursor converts UTF-8 input to folded UTF-16 code units using ICU `U8_NEXT`, `u_foldCase()`, and `U16_APPEND`, while recording original UTF-8 byte offsets. It then opens an ICU word break iterator over the UTF-16 buffer. `icuNext()` advances to the next non-whitespace word boundary range, converts that UTF-16 token back to UTF-8 with `u_strToUTF8()`, grows the output buffer if needed, and returns token text and original byte offsets.

## State and persistence

All state is per-tokenizer or per-cursor heap state. No SQLite tables are modified. The cursor owns the break iterator, UTF-16 input, offset array, and UTF-8 output buffer until `icuClose()`.

## Dependencies and integration points

Depends on ICU headers `ubrk.h`, `ucol.h`, `ustring.h`, `utf16.h`, and the common FTS tokenizer ABI from `fts3_tokenizer.h`. It integrates through tokenizer registration in FTS module setup and can be used by expression parsing, indexing, snippet generation, and offsets wherever a tokenizer is required.

## Risks and test signals

Build risk is high because this code is excluded unless ICU support is enabled. Runtime risks include invalid UTF-8 conversion to replacement characters, ICU status failures, offset mapping around supplementary codepoints, whitespace-only boundary ranges, and allocation loops around `u_strToUTF8()`. Signals are tokenizer tests with locale arguments, multilingual text, folded case, byte-offset assertions, and ICU-enabled build coverage.
