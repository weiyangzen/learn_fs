# sources/storage-engines/sqlite/ext/fts3/fts3_test.c

## Purpose

Provides Tcl-only FTS3/FTS4 test helpers. It validates NEAR matching logic, exposes knobs for incremental doclist loading, returns a version-1 tokenizer for language-id tests, tests FTS varints, and toggles debug corruption assertions.

## Important APIs, types, and functions

NEAR test structures are `NearDocument`, `NearToken`, and `NearPhrase`, with helpers `nm_phrase_match()`, `nm_near_chain()`, and `nm_match_count()`. Tcl commands include `fts3_near_match_cmd()`, `fts3_configure_incr_load_cmd()`, `fts3_test_tokenizer_cmd()`, `fts3_test_varint_cmd()`, and `fts3_may_be_corrupt()`. The test tokenizer uses `test_tokenizer`, `test_tokenizer_cursor`, and callbacks including `testTokenizerLanguage()`. `Sqlitetestfts3_Init()` registers all commands.

## Control flow

`fts3_near_match` parses document and expression Tcl lists, builds phrase arrays, and checks phrase occurrences plus forward/reverse NEAR chains. The incremental-load command returns current global tuning values and optionally overwrites them. The test tokenizer emits alphabetic ASCII tokens, lowercasing for even language ids, preserving case for odd ids, and returning an error for language ids >=100. Varint testing round-trips values through FTS varint encoders/decoders.

## State and persistence

No database state is persisted. The file mutates test-only globals `test_fts3_node_chunksize`, `test_fts3_node_chunk_threshold`, and, under debug, `sqlite3_fts3_may_be_corrupt`. Tcl allocations are command-local, and tokenizer cursor buffers are heap-owned.

## Dependencies and integration points

Depends on `tclsqlite.h`, `fts3Int.h`, SQLite FTS varint helpers, and the tokenizer ABI. It integrates only into testfixture builds with `SQLITE_TEST` and FTS3/FTS4 enabled.

## Risks and test signals

Risks are mostly test-harness drift: NEAR semantics here must match production evaluation, tokenizer language-id behavior must exercise `xLanguageid`, and global tuning changes must be restored by tests. Signals are Tcl command results, phrase-count variable output, varint round-trip failures, language-id error propagation, and debug corruption assertion toggling.
