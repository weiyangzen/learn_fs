# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/gbk_collation.rs

## Purpose
Implements `gbk_bin` and `gbk_chinese_ci` collators using generated BMP-sized GBK weight tables.

## APIs, Flow, And State
The private `GbkCollator` trait supplies case-insensitive status, invalid-rune truncation policy, and a weight table. A blanket `Collator` implementation decodes UTF-8 characters, maps them to `u16` weights, writes variable-width sort keys, compares weight streams, and hashes weights after trimming padding. `CollatorGbkBin` is case-sensitive and substitutes `?` for invalid UTF-8. `CollatorGbkChineseCi` is case-insensitive and truncates comparison/hash/sort-key generation at invalid UTF-8.

## Dependencies And Integration
Depends on `CharsetGbk`, shared collation helpers, `BufferWriter`, `Hasher`, and included data files `gbk_bin.data` and `gbk_chinese_ci.data`. Integrated through `match_template_collator!`.

## Risks And Test Signals
Risks are table-generation correctness, invalid-character policy, and the assumption that stored GBK text arrives as UTF-8. Shared collation tests cover Chinese ordering, invalid runes, padding, sort keys, and hash equality.
