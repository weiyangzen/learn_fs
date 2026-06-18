# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/gb18030_collation.rs

## Purpose
Implements `gb18030_bin` and `gb18030_chinese_ci` collators using generated Unicode-to-GB18030 weight tables.

## APIs, Flow, And State
`CollatorGb18030Bin` and `CollatorGb18030ChineseCi` implement `Collator` with `CharsetGb18030` and `u32` weights. `char_weight` indexes included four-byte tables by Unicode scalar. Sort-key writers trim padding, decode UTF-8, and emit big-endian one-, two-, or four-byte weights. The binary variant maps invalid UTF-8 bytes to `?`; the Chinese case-insensitive variant truncates on invalid sequences. `sort_compare` and `sort_hash` mirror those invalid-sequence policies and compare/hash weights directly.

## Dependencies And Integration
Depends on shared collation helpers, buffer writer/reader traits, and included data files `gb18030_bin.data` and `gb18030_chinese_ci.data`. It is selected through the collation macro for GB18030 collations.

## Risks And Test Signals
Risks include large table correctness, byte-order compatibility with TiDB/MySQL sort keys, and invalid UTF-8 policy differences between bin and Chinese CI variants. Tests verify representative weights; shared collator tests verify compare, hash, and sort key output.
