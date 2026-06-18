# sources/storage-engines/tikv/components/tidb_query_common/src/util.rs

## Purpose
Implements byte-prefix range helpers used by TiDB/TiKV coprocessor storage paths to detect point ranges and build exclusive prefix upper bounds.

## APIs, Flow, And State
`convert_to_prefix_next` mutates a key to the smallest lexicographically greater key representing the next prefix. Empty input becomes `[0]`; trailing `0xFF` bytes carry to zero; all-`0xFF` input appends a trailing zero after restoring the original bytes to `0xFF`. `is_prefix_next` checks whether `next` is exactly that transformation, including same-length carry cases and all-`0xFF` length-plus-one cases. `is_point` applies the check to a `kvproto::coprocessor::KeyRange` start/end pair.

## Dependencies And Integration
The file depends only on `kvproto::coprocessor::KeyRange`. It is used by query common storage/range logic to identify encoded point gets versus interval scans without decoding higher-level row keys.

## Risks And Test Signals
These helpers sit on range-boundary correctness, so off-by-one behavior could turn point reads into range scans or miss rows at prefix boundaries. Unit tests cover empty keys, normal increment, trailing carries, all-`0xFF` expansion, and many negative `is_prefix_next` examples.
