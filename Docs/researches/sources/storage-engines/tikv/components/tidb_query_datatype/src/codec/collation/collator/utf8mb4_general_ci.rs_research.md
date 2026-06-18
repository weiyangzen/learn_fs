# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_general_ci.rs

## Purpose
Implements `utf8mb4_general_ci`, a case-insensitive UTF-8 collation using static Unicode-plane weight tables.

## APIs, Flow, And State
`CollatorUtf8Mb4GeneralCi` uses `CharsetUtf8mb4` and `u16` weights. `char_weight` maps code points above BMP to replacement weight `0xFFFD`; BMP code points consult a sparse plane table and fall back to the code point when no plane override exists. `write_sort_key` trims padding, decodes UTF-8 with `next_utf8_char`, writes big-endian weights, and stops at invalid bytes. `sort_compare` compares decoded weight streams and returns equality on invalid UTF-8. `sort_hash` hashes the same weights after padding trim.

## Dependencies And Integration
Depends on shared collation helpers, buffer writer traits, and the `Collator` trait. It is selected through `match_template_collator!` and used by string comparison, hashing, and sort-key paths for `utf8mb4_general_ci`.

## Risks And Test Signals
Risks are static table correctness, incomplete Unicode equivalence relative to newer UCA collations, and invalid UTF-8 truncation/equality behavior. Shared tests cover case folding, accent examples, non-BMP fallback, padding, exact sort keys, and hash consistency for equal comparisons.
