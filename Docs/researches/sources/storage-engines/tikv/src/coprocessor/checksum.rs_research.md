# sources/storage-engines/tikv/src/coprocessor/checksum.rs

Purpose: handles TiDB checksum requests over MVCC snapshots. `ChecksumContext<S>` owns a `ChecksumRequest` and a `RangesScanner<TikvStorage<SnapshotStore<S>>, ApiV1>` that scans key/value rows across requested ranges.

Important APIs: `ChecksumContext::new` builds a `SnapshotStore` with request isolation, fill-cache, bypass-lock, and access-lock settings, then wraps it in `TikvStorage` and `RangesScanner`. `handle_request` currently accepts only `ChecksumAlgorithm::Crc64Xor`, applies optional old/new prefix rewrite rules, scans all rows, verifies scanned keys start with the expected new prefix, computes xor CRC64 values through `checksum_crc64_xor`, and serializes `ChecksumResponse`. `collect_scan_statistics` forwards scanner storage stats.

State and persistence: all state is request-local. It reads from a snapshot but writes no persisted data. Dependencies include protobuf `ChecksumRequest/Response`, `crc64fast`, `tidb_query_common::RangesScanner`, and TiKV storage abstractions.

Integration points: built by `Endpoint::parse_request_and_check_memory_locks_impl` for `REQ_TYPE_CHECKSUM`; checksum requests are allowed during flashback. Risks include prefix-length arithmetic (`old_prefix.len() - new_prefix.len()`), unsupported algorithms, and strict ApiV1 storage format. Test signals are indirect; `checksum_crc64_xor` is exported from `mod.rs`, but this file has no local test module.
