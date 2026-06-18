# sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer.h

## Purpose

Defines the stable FTS3 tokenizer ABI used by built-in tokenizers, optional external tokenizers, and FTS query/index/snippet code.

## Important APIs, types, and functions

Declares `sqlite3_tokenizer_module`, `sqlite3_tokenizer`, and `sqlite3_tokenizer_cursor`. Module callbacks are `xCreate`, `xDestroy`, `xOpen`, `xClose`, `xNext`, and version-1 `xLanguageid`. The base tokenizer stores `pModule`; the base cursor stores `pTokenizer`. The header also declares test helper symbols `fts3_global_term_cnt()` and `fts3_term_cnt()`.

## Control flow

An FTS table resolves a module, calls `xCreate()` with tokenizer arguments, and later opens cursors with `xOpen()` for specific input buffers. `xNext()` returns normalized token text, byte offsets in the original input, and token position until `SQLITE_DONE`. If `iVersion>=1`, FTS may call `xLanguageid()` after opening the cursor.

## State and persistence

The ABI itself stores no data beyond base struct pointers. Tokenizer implementations extend the structs with private state. The normalized tokens produced through this interface are persisted indirectly in FTS indexes and used for query normalization.

## Dependencies and integration points

Includes `sqlite3.h` for result codes and integer types. Implemented by `fts3_tokenizer1.c`, `fts3_porter.c`, `fts3_unicode.c`, `fts3_icu.c`, and test tokenizers. Consumed by parser, index writer, snippet/offset code, `fts3tokenize`, and tokenizer registration.

## Risks and test signals

The ABI requires input buffers to remain valid until `xClose()` and returned token buffers to remain valid only until next `xNext()` or close. Incorrect offsets break snippets and offsets. Version negotiation for `xLanguageid()` must be respected. Test signals are lifecycle tests, tokenizer output tests, language-id behavior, and offset-sensitive snippets.
