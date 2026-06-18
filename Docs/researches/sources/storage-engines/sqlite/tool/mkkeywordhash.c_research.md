# sources/storage-engines/sqlite/tool/mkkeywordhash.c

## Purpose

Build-time generator for SQLite's SQL keyword lookup code. It starts from the static keyword list, applies `SQLITE_OMIT_*` and feature masks, compresses keyword text, chooses a compact hash table, and prints C code implementing `keywordCode()`, `sqlite3KeywordCode()`, `sqlite3_keyword_name()`, `sqlite3_keyword_count()`, and `sqlite3_keyword_check()`.

## Important APIs, control flow, and dependencies

The central type is `Keyword`, which carries the keyword spelling, token symbol, feature mask, priority, generated hash-chain data, compressed-text offsets, substring embedding metadata, and original spelling. `keywordCompare1()`, `keywordCompare2()`, and `keywordCompare3()` drive the successive qsort passes. `findById()` resolves substring parents, and `reorder()` promotes higher-priority keywords within hash collision chains. `main()` filters disabled keywords, computes hashes using `charMap()` and `HASH_C0/HASH_C1/HASH_C2`, detects embedded keywords and reusable suffix/prefix text, searches hash-table sizes from half to twice the keyword count, then emits arrays and lookup functions to stdout.

## State, persistence, and integration

The program persists nothing itself; its only durable output is generated C source captured by the SQLite build. It depends on parser token names such as `TK_SELECT`, SQLite feature macros, ASCII/EBCDIC branches in generated code, and public keyword APIs expected by SQLite clients. The generated lookup assumes tokens of length at least two for the internal path and returns `TK_ID` for non-keywords through `sqlite3KeywordCode()`.

## Risks and test signals

Risk concentrates in generator determinism and semantic drift: a keyword token or feature mask mismatch changes parser behavior, a bad compression offset corrupts `sqlite3_keyword_name()`, and a weak hash/priority ordering can increase lookup cost or alter token precedence for common keywords. Useful signals are regenerating the keyword source and diffing it, parser tests for all SQL grammar feature combinations, keyword API tests for count/name/check, and builds under omitted features plus ASCII/EBCDIC configurations.
