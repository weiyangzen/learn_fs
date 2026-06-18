# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_binary.rs

## Purpose
Implements UTF-8 binary collations with and without padding behavior.

## APIs, Flow, And State
`CollatorUtf8Mb4Bin` trims trailing padding spaces for sort keys, comparisons, and hashes unless `force_no_pad` is requested for comparison. `CollatorUtf8Mb4BinNoPadding` writes, compares, and hashes raw bytes without trimming. Both use `CharsetUtf8mb4`, Unicode scalar numeric weights, and case-sensitive semantics, but their sort operations are byte-based rather than weight-stream based.

## Dependencies And Integration
Depends on shared collation helpers and the `Collator` trait. `Utf8Mb4Bin`, `Utf8Mb4BinNoPadding`, and `Utf8Mb40900Bin` selection flows through `match_template_collator!`, with 0900 binary mapped to the no-padding implementation.

## Risks And Test Signals
Padding behavior is the key risk: the two types intentionally diverge for strings differing only by trailing spaces. Shared tests cover this distinction in compare, hash, and sort-key expectations.
