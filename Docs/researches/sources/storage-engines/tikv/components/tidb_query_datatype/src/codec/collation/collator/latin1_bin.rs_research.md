# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/latin1_bin.rs

## Purpose
Implements `latin1_bin` collation with SQL padding behavior.

## APIs, Flow, And State
`CollatorLatin1Bin` uses `CharsetBinary`, byte weights, and case-sensitive semantics. `write_sort_key` trims trailing padding spaces before writing bytes. `sort_compare` trims trailing spaces unless `force_no_pad` is set, then uses byte comparison. `sort_hash` hashes the trimmed bytes so equal padded values hash equally.

## Dependencies And Integration
Depends on `bstr` trimming helpers, shared `PADDING_SPACE`, `BufferWriter`, and the `Collator` trait. It is selected through the collation macro for `Collation::Latin1Bin`.

## Risks And Test Signals
Main risk is padding semantics: only ASCII space is trimmed, while other trailing bytes remain significant. Dedicated tests in the collator module cover equal padded values and non-space trailing bytes.
