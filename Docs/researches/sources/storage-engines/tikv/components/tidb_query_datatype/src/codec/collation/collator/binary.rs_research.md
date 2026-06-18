# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/binary.rs

## Purpose
Implements the raw binary collation without padding semantics.

## APIs, Flow, And State
`CollatorBinary` uses `CharsetBinary`, byte weights, case-sensitive behavior, raw byte sort keys, direct byte-slice comparison, and raw byte hashing. It does not trim trailing spaces and ignores `force_no_pad` because binary collation is already no-padding here.

## Dependencies And Integration
Implements the shared `Collator` trait and is selected by `match_template_collator!` for `Collation::Binary`. It underpins binary string comparisons, sort keys, and hash semantics.

## Risks And Test Signals
The implementation is intentionally simple; risk is semantic mismatch with SQL padding expectations if used for a padded collation. Shared collation tests compare ordering, sort key, and hash equality behavior.
