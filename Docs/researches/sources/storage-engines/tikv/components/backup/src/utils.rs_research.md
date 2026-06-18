# sources/storage-engines/tikv/components/backup/src/utils.rs

## Purpose
Holds backup utility logic for API-version-aware key/value conversion and runtime construction. The central type, `KeyValueCodec`, normalizes transactional and RawKV backup keys and values across TiKV API versions.

## APIs, Types, And Functions
`BACKUP_V1_TO_V2_TS` is the synthetic causal timestamp used when converting RawKV V1/V1ttl to API V2. `KeyValueCodec` stores whether the operation is RawKV plus current and destination API versions. Its methods validate supported conversions, encode backup ranges, decode response keys, convert encoded raw keys/values to the destination version, validate raw values for deletion/TTL, and detect whether RawKV V2 should use MVCC snapshots. `create_tokio_runtime` creates a multi-thread tokio runtime with export I/O hooks.

## Control Flow
Backup callers construct the codec, call `check_backup_api_version`, encode request ranges, scan data, filter raw values with `is_valid_raw_value`, convert key/value encodings, and decode user-facing response ranges. The conversion paths use `dispatch_api_version!` so version-specific behavior is delegated to the `api_version` crate.

## State And Persistence
The codec is stateless after construction. It does not persist data; it determines how backup entries are represented on disk by downstream writers. Runtime creation sets thread-local file-system I/O type to `Export`, affecting accounting/classification for work executed on that runtime.

## Dependencies And Integration Points
Integrates with `api_version`, `kvproto::kvrpcpb::ApiVersion`, `txn_types::Key/TimeStamp`, file-system I/O classification, and tokio. `writer.rs` uses the codec when writing RawKV SSTs and computing checksums from decoded destination keys/values.

## Risks And Test Signals
Risks center on API-version boundary mistakes: accepting invalid V2 raw ranges, backing up deleted or expired values, or producing incompatible V2 encodings. Tests cover allowed and rejected conversion combinations, backup key encode/decode, V1/V1ttl/V2 key/value conversion, and TTL/delete validity.
