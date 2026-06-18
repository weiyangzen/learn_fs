# sources/object-store/rustfs/crates/ecstore/src/disk/format.rs

## Purpose
`format.rs` models the `format.json` metadata stored on RustFS erasure disks. It defines versioned metadata enums, backend kind, erasure set layout, deployment id, disk id membership, JSON parsing/serialization, and validation helpers used during store initialization and disk membership checks.

## Important APIs, Types, And Functions
- `FormatMetaVersion` currently supports `"1"` plus `Unknown`.
- `FormatBackend` supports `"xl"` erasure and `"xl-single"` single-disk erasure, plus `Unknown`.
- `FormatErasureV3` stores erasure format version, this disk's UUID, the two-dimensional set/disk UUID layout, and distribution algorithm.
- `FormatErasureVersion` recognizes `"1"`, `"2"`, and `"3"`.
- `DistributionAlgoVersion` recognizes `"CRCMOD"`, `"SIPMOD"`, and `"SIPMOD+PARITY"`.
- `FormatV3` is the top-level format document with metadata version, backend, deployment id, erasure section, and skipped runtime `disk_info`.
- `TryFrom<&[u8]>` and `TryFrom<&str>` parse JSON into `FormatV3`.
- `FormatV3::new` creates a new deployment format with generated UUIDs and V3 distribution.
- `drives`, `to_json`, `find_disk_index_by_disk_id`, and `check_other` provide layout utility and validation.

## Control Flow
`FormatV3::new` chooses `xl-single` when `set_len == 1`, otherwise `xl`. It generates a deployment id, nil `this` id, and `num_sets * set_len` random disk UUIDs. The caller later assigns each disk's `erasure.this` before saving.

Parsing is direct Serde JSON parsing. Unknown tagged enum values deserialize to `Unknown` rather than failing, but required fields and UUID formats still must parse. `find_disk_index_by_disk_id` rejects nil as `DiskNotFound`, rejects max UUID as an offline placeholder, then scans the `sets` matrix for a matching disk id and returns `(set_idx, disk_idx)`.

`check_other` validates that another disk's format has the same set count, same set sizes, and identical UUIDs in every position. It temporarily ignores `other.erasure.this` while comparing layout, then confirms that `this` exists somewhere in the layout. This makes it a membership check against a reference format, not just schema validation.

## State And Persistence Behavior
This file describes persistent disk state. `FormatV3` is serialized into `format.json` under the RustFS metadata bucket. Its fields identify deployment membership, erasure set geometry, disk position, and object distribution algorithm. `disk_info` is skipped during serialization and is runtime-only.

Changing enum serialization names, field names, or layout semantics would affect compatibility with existing disks and MinIO/RustFS migration paths. The code already parses older erasure versions and distribution algorithms in tests, while new format creation emits V3 and `SIPMOD+PARITY`.

## Dependencies And Integration Points
`disk/local.rs` reads `format.json`, parses `FormatV3`, calls `find_disk_index_by_disk_id`, and maps malformed/missing format through `error_conv.rs`. `store_init.rs` creates new formats, migrates existing formats, finds quorum format, validates erasure values, loads all formats, and saves format files. `set_disk.rs`, `sets.rs`, and `set_disk/lock.rs` store and compare `FormatV3` to connect endpoints and identify disk positions. `config/com.rs` and tests use `FormatV3::new` to build fake layouts.

The module depends on `serde`, `serde_json`, `uuid`, `DiskInfo`, and `DiskError`.

## Risks And Edge Cases
- Unknown enum variants deserialize without immediate failure. That helps forward compatibility, but callers must validate if unknown versions/backends are unacceptable.
- `check_other` error messages include a Go-style `(%w)` fragment in a formatted string without wrapping semantics.
- `find_disk_index_by_disk_id` treats nil and max UUID specially; misuse of those sentinels could misclassify an actual layout issue as disk not found or offline.
- `FormatV3::new` creates random UUIDs for every layout position, so tests or callers needing stable layouts must override generated IDs explicitly.
- Any change to serialized field names such as `distributionAlgo` or `xl` is persistent-format sensitive.

## Test Signals
Tests cover creation of single and multi-disk formats, drive counts, JSON serialization content, parsing from string and bytes for older and current erasure versions, invalid JSON, disk-index lookup success and nil/max/not-found failures, reference-format comparison for identical and mismatched layouts, enum serialization/deserialization including `Unknown`, distribution algorithm serialization, and round-trip serialization.
