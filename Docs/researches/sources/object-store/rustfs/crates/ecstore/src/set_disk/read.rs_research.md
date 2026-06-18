# sources/object-store/rustfs/crates/ecstore/src/set_disk/read.rs

## Purpose
Implements set-level metadata and data reads for erasure-coded objects. It reads file metadata across disks, chooses quorum object state, reads multipart part metadata, batches small multi-file reads, and streams object ranges by decoding erasure shards.

## Important APIs, Types, And Functions
Collector helpers `collect_read_multiple_results` and `collect_read_parts_results` run early-quorum `JoinSet` tasks. `read_parts`, `read_all_fileinfo`, `read_version_optimized`, `read_all_xl`, `read_all_raw_file_info`, `pick_latest_quorum_files_info`, `read_multiple_files`, `get_object_fileinfo`, `get_object_info_and_quorum`, and `get_object_with_fileinfo` make up the read surface.

## Control Flow
Metadata reads fan out to all disks with `read_version` or raw xl reads, merge versions, and reduce errors to a quorum-selected `FileInfo`. `get_object_fileinfo` computes read quorum, reduces errors, selects online disks by common metadata, picks valid file info, and enqueues background heal if any disk had metadata errors. `get_object_with_fileinfo` validates byte-range bounds, maps offsets to parts, creates bitrot readers for the required erasure shard ranges, checks that available shards meet data quorum, optionally enqueues heal for missing shards, and calls `erasure.decode` into the caller’s async writer.

## State And Persistence Behavior
Read operations are mostly non-mutating, but they can enqueue heal requests when metadata or data shard gaps are detected. The object stream itself is reconstructed from persisted part files and optional inline metadata bytes. Zero-copy behavior is controlled by `ENV_OBJECT_ZERO_COPY_ENABLE`.

## Dependencies And Integration Points
This file integrates disk `read_version`, `read_xl`, `read_multiple`, and `read_parts`; `FileMeta` version merging; quorum helpers; erasure coding; bitrot readers; object error mapping; heal channel; and processor pools.

## Risks
Index alignment across shuffled disks, `files`, and erasure distribution is critical. `files[idx].data_dir.unwrap_or_default()` can silently form paths with an empty data dir for bad metadata. `read_version_optimized` uses `self.format.erasure.sets.len()` as `required_reads`, which is set count rather than per-set data quorum and should be reviewed before relying on it broadly.

## Test Signals
Tests cover early failure and panic tolerance for both multi-file and part-read collectors. More integration tests are needed for range reads across part boundaries, background heal enqueue, inline data, legacy checksum selection, and versioned delete-marker behavior.
