# sources/storage-engines/tikv/components/raftstore/src/store/snap/io.rs

## Purpose

Provides the concrete file IO routines used by `snap.rs`: build snapshot CF files from an engine snapshot, encode/decode the plain lock-CF format, build and verify SST files for default/write CFs, apply snapshots either by direct writes or external SST ingestion, enforce read IO throttling during SST generation, and open decrypting readers for encrypted snapshot files.

## Important APIs, Types, And Functions

`StaleDetector` abstracts cancellation for apply loops. `BuildStatistics` reports key count, logical KV bytes, generated SST bytes, plain-file bytes, and measured read IO bytes. `build_plain_cf_file` writes compact-length key/value pairs plus an empty-key sentinel for the plain format. `build_sst_cf_file_list` writes Zstd-compressed SST files, splitting when the raw key/value size exceeds `raw_size_per_file`, verifying block checksums through `SstReader`, syncing finished files, and tracking IO limiter consumption. `apply_plain_cf_file` decodes the plain format into write batches and invokes a callback after each batch. `apply_sst_cf_files_by_ingest` ingests prepared SSTs with an optional region key range and forced allow-write. `apply_sst_cf_files_without_ingest` and its helper iterate SST contents and write them to the KV engine in batches. `get_decrypter_reader` opens a plaintext or decrypting reader based on `DataKeyManager` file metadata.

## Control Flow

Plain build opens a new temp file, optionally wraps it in `EncrypterWriter`, scans the requested CF/range from the engine snapshot, compact-encodes every key and value, and syncs only if at least one key was found. Empty scans remove the temp file and leave `CfFile` without file entries. SST build creates the first temp SST writer, scans the CF/range, and rotates to a new SST when adding the next entry would exceed the raw-size budget. On rotation, it records the previous file in `CfFile`, finishes and verifies the old SST, syncs it, and then continues with the new writer. After scan completion it handles any remaining measured read IO, finishes/verifies the final SST if non-empty, records its path, and deletes the unused temp file if empty.

Apply by direct write uses the same batching pattern for plain and SST formats: read or iterate records, check `StaleDetector` before each item loop, accumulate `(key, value)` pairs until `batch_size`, write them to a reusable engine write batch, clear the batch, call the provided callback, and continue. Plain apply stops on the empty-key sentinel. SST direct apply stops when the SST iterator becomes invalid. Ingest apply delegates to `KvEngine::ingest_external_file_cf`, passing the snapshot region range and `force_allow_write = true`; comments document why overlapping foreground writes should not exist during snapshot apply.

## State And Persistence Behavior

This file does not own long-lived state. It creates, writes, verifies, syncs, removes, and reads snapshot temp files supplied by `CfFile`. For encrypted files, file encryption metadata is created by callers during receive/build setup; this helper either wraps writers or opens decrypting readers using that metadata. `BuildStatistics` is transient but feeds snapshot metrics in `snap.rs`. Batch writes during apply are durable according to the underlying engine write semantics, while comments note that callers remain responsible for flushing/syncing CFs after direct apply.

## Dependencies And Integration Points

Depends on `engine_traits` for snapshots, scanning, SST writer/reader/builders, iterators, write batches, ranges, and compression selection. It uses `file_system` for IO type guards, files, open options, and IO byte tracking; `tikv_util::Limiter` for throttling; `txn` byte codecs for plain snapshot encoding; `encryption` for encrypting/decrypting streams; and `fail` failpoints for corruption and IO tests. It is called almost exclusively by `snap.rs`, which chooses plain format for `CF_LOCK`, SST format for other snapshot CFs, and decides between ingest and direct apply.

## Risks

Correctness depends on matching build and apply formats exactly: plain files rely on an empty-key sentinel and compact byte framing, while SST files rely on engine SST semantics. `build_sst_cf_file_list` only limits measured read IO at intervals, and the TODO notes snapshot file write IO is not part of that limiter. The file split threshold is based on raw key/value bytes, not compressed SST bytes, so actual disk sizes vary. The ingest path uses `force_allow_write`; its safety relies on raftstore region worker ordering, unapplied snapshot state, and ingest latch behavior documented in comments. Direct apply can be aborted between batches; callers must handle partially applied state according to the broader snapshot apply protocol. Corruption detection depends on SST block checksum verification and later size/checksum validation in `snap.rs`.

## Test Signals

Tests build and apply plain files across empty/non-empty and encrypted/non-encrypted DBs, verifying callback-collected keys match engine scans. SST tests cover empty/non-empty builds, encryption, multi-file splitting, clone/tmp/path metadata lengths, ingestion into a destination DB, and data equality. The failpoint-gated IO limiter test verifies measured read IO and elapsed time under a mocked read-byte counter. These tests directly exercise the encoding, split, encryption reader/writer, ingestion, and throttling paths.
