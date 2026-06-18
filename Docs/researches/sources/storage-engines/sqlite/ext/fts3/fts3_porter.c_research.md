# sources/storage-engines/sqlite/ext/fts3/fts3_porter.c

## Purpose

Implements the built-in Porter stemming tokenizer. It tokenizes ASCII-like words, folds ASCII case, and stems English terms for FTS matching while leaving unsupported or long tokens to a copy/truncation fallback.

## Important APIs, types, and functions

`porter_tokenizer` is the tokenizer instance and `porter_tokenizer_cursor` tracks input, offsets, token index, and reusable output buffer. Tokenizer callbacks are `porterCreate()`, `porterDestroy()`, `porterOpen()`, `porterClose()`, and `porterNext()`. Stemming helpers include `isConsonant()`, `isVowel()`, `m_gt_0()`, `m_eq_1()`, `m_gt_1()`, `hasVowel()`, `doubleConsonant()`, `star_oh()`, `stem()`, `copy_stemmer()`, and `porter_stemmer()`. `sqlite3Fts3PorterTokenizerModule()` exports the module.

## Control flow

`porterNext()` scans past delimiters, collects a token, grows `zToken` as needed, and passes the raw token to `porter_stemmer()`. The stemmer reverses lower-case ASCII letters into a fixed buffer, applies Porter steps 1a through 5b using reversed suffix matching, then reverses the stem back. Tokens that are too short, too long, contain digits, or contain non-ASCII letters fall back to case-folded copying and possible truncation.

## State and persistence

State is transient tokenizer/cursor memory only. Index persistence is indirect: because indexed terms are stemmed, changing this algorithm or delimiter rules would require reindexing existing FTS data.

## Dependencies and integration points

Uses the FTS tokenizer ABI and SQLite allocation APIs. It is registered as a tokenizer module and is consumed by FTS table creation, query parsing, indexing, snippets, offsets, and `fts3tokenize`.

## Risks and test signals

Risks include English-specific stemming surprises, fixed-size reverse buffer boundaries, inconsistent handling of high-bit UTF-8 bytes as token characters but not stemmable letters, and term-collision effects from fallback truncation. Test signals are known Porter stem output, offset preservation after stemming, delimiter behavior, long-token truncation, non-ASCII fallback, and tokenizer-module lifecycle tests.
