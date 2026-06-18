# sources/storage-engines/sqlite/ext/fts5/fts5_tokenize.c

## Purpose
`fts5_tokenize.c` implements and registers FTS5 built-in tokenizers: `unicode61`, `ascii`, `trigram`, and the v2 `porter` tokenizer wrapper. It turns SQL tokenizer declarations into `Fts5Tokenizer` instances, folds text, handles token/separator customization, emits tokens through FTS5 callbacks, and reports pattern support for trigram-backed LIKE/GLOB acceleration.

## Important APIs, Types, And Functions
The exported integration points are `sqlite3Fts5TokenizerInit()`, `sqlite3Fts5TokenizerPattern()`, and `sqlite3Fts5TokenizerPreload()`. `sqlite3Fts5TokenizerInit()` registers tokenizer modules with the `fts5_api`; `sqlite3Fts5TokenizerPattern()` identifies trigram pattern capability; `sqlite3Fts5TokenizerPreload()` detects configurations that must instantiate trigram tokenizers before planning.

Important tokenizer state types are `AsciiTokenizer`, `Unicode61Tokenizer`, `PorterTokenizer`, `PorterContext`, and `TrigramTokenizer`. ASCII stores a 128-byte token-character table. Unicode stores ASCII token flags, a reusable folding buffer, diacritic mode, sorted non-ASCII exceptions, and Unicode category flags. Porter wraps another tokenizer and stems callback tokens. Trigram stores case-fold and diacritic-fold flags.

## Control Flow
Registration builds an array for `unicode61`, `ascii`, and `trigram`, calls `xCreateTokenizer()` for each, then registers `porter` with the v2 tokenizer interface. ASCII tokenization skips ASCII separators, treats non-ASCII bytes as token bytes, lowercases ASCII, and calls `xToken()` with original byte offsets. Unicode tokenization parses UTF-8, uses category tables from `fts5_unicode2.c`, folds with `sqlite3Fts5UnicodeFold()`, and optionally removes diacritics. Porter delegates to a base tokenizer and stems callback tokens with generated Porter steps. Trigram emits overlapping 3-character folded tokens and advertises LIKE or GLOB pattern support depending on case sensitivity.

## State And Persistence
All state is per-tokenizer instance and heap-owned by SQLite. There is no direct disk persistence. Effects become persistent only through FTS5 callers that store emitted tokens in an index. Unicode folding buffers are retained between calls, and Porter retains the base tokenizer.

## Dependencies And Integration Points
The file depends on `fts5Int.h`, FTS5 tokenizer APIs, SQLite allocation/string utilities, FTS5 pattern constants, and Unicode helper functions from `fts5_unicode2.c`. Token callbacks integrate with FTS5 indexing, querying, auxiliary functions, and query planning for trigram LIKE/GLOB.

## Risks
UTF-8 boundary handling and byte offsets are critical for phrase and snippet features. Unicode category, exception, and diacritic options change token boundaries. ASCII intentionally treats non-ASCII bytes as token characters. Porter stemming assumes short lowercased ASCII-like tokens. Trigram rejects `remove_diacritics` with `case_sensitive=1`, which should stay covered by tests.

## Test Signals
Cover tokenizer option parsing, tokenchars/separators overrides, Unicode categories, diacritic modes, malformed UTF-8, offset correctness, Porter expected stems, trigram LIKE/GLOB planning, and `SQLITE_DONE` callback normalization.
