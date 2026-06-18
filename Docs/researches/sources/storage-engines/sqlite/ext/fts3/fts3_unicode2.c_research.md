# sources/storage-engines/sqlite/ext/fts3/fts3_unicode2.c

## Purpose

Contains machine-generated Unicode classification, diacritic, and case-folding tables used by the Unicode tokenizer. The file explicitly says not to edit it by hand.

## Important APIs, types, and functions

Public functions are `sqlite3FtsUnicodeIsalnum()`, `sqlite3FtsUnicodeIsdiacritic()`, and `sqlite3FtsUnicodeFold()`. Internal `remove_diacritic()` maps many Latin lowercase diacritic codepoints to ASCII base letters. The implementation uses compact range tables and binary searches.

## Control flow

`sqlite3FtsUnicodeIsalnum()` handles ASCII with bitmasks and non-ASCII by finding the last generated non-alnum range not greater than the target codepoint. `sqlite3FtsUnicodeIsdiacritic()` checks a compact mask for combining marks U+0300 through U+0331. `sqlite3FtsUnicodeFold()` first applies ASCII or generated Unicode lowercase mappings, handles a supplementary Deseret range, and then optionally calls `remove_diacritic()`. Diacritic mode 2 enables mappings marked complex that mode 1 preserves.

## State and persistence

The file has only static read-only tables. It persists nothing directly, but table contents determine normalized tokens stored in FTS indexes. Regenerating against a different Unicode database can change query/index compatibility.

## Dependencies and integration points

Compiled when Unicode FTS3 support is enabled. Consumed by `fts3_unicode.c` for token boundary classification, combining-mark treatment, and token normalization. Generated from Unicode data files under the `unicode/` directory according to comments and tool scripts.

## Risks and test signals

Risks include stale generated data, binary-search boundary mistakes, differing behavior for complex diacritic mappings, undefined behavior for negative codepoints, and index drift if tables change. Test signals are generated-table conformance tests, known fold/diacritic examples, ASCII fast-path coverage, combining-diacritic handling, and tokenizer regression tests over multilingual samples.
