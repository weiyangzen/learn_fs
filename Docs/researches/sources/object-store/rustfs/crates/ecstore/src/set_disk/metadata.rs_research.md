# sources/object-store/rustfs/crates/ecstore/src/set_disk/metadata.rs

## Purpose
Implements metadata consensus and erasure-layout helpers for set-disk operations. It decides whether an object has read/write quorum, which metadata version is authoritative, and how disks and metadata should be reordered to match erasure distribution.

## Important APIs, Types, And Functions
Key functions include `all_not_found_metadata`, `reduce_common_data_dir`, multipart path helpers `get_upload_id_dir` and `get_multipart_sha_dir`, `common_parity`, `object_quorum_from_meta`, `list_online_disks`, `pick_valid_fileinfo`, `find_file_info_in_quorum`, `shuffle_disks_and_parts_metadata_by_index`, `shuffle_disks_and_parts_metadata`, `shuffle_parts_metadata`, `shuffle_disks`, and `shuffle_check_parts`.

## Control Flow
Quorum computation first handles all-not-found metadata, reduces read errors, derives per-disk parity from valid metadata, selects the common parity that itself has quorum, then returns data and write quorum. Online disk selection finds a common mod time, or falls back to common ETag when mod-time quorum is unavailable. `find_file_info_in_quorum` filters valid metadata by the common selector, hashes part numbers/sizes and erasure layout, requires a hash quorum, and returns a representative `FileInfo` with quorum-agreed version properties.

## State And Persistence Behavior
This file does not write persistent state. It interprets persisted xl metadata (`FileInfo`) and maps it onto in-memory disk positions. Multipart upload IDs are decoded from URL-safe base64 where possible and mapped into the deterministic SHA-256 multipart directory.

## Dependencies And Integration Points
It is used by read, write, multipart, and heal paths. It depends on `DiskError` reducers, `FileInfo`, `OffsetDateTime`, `Uuid`, SHA-256 hashing, and object property structs.

## Risks
Tie-breaking in `common_time_and_occurrence` chooses the latest timestamp when counts tie, which affects authoritative version selection. Metadata hashing omits some TODO fields such as remote, encrypted, and compressed details, so future metadata variants need careful expansion. Shuffle helpers assume one-based erasure indices and valid distribution lengths.

## Test Signals
No tests in this file, but many downstream tests rely on it. Focused tests should cover parity selection for delete markers, ETag fallback, conflicting metadata hashes, distribution mismatch fallback, and upload-id decoding compatibility.
