# sources/storage-engines/tikv/src/server/tablet_snap.rs

## Purpose

This module implements sending and receiving tablet snapshots for raftstore v2. Unlike older snapshot transfer that creates new files, tablet snapshots transfer engine data in its original file form and can reuse receiver-side cached SST files by comparing previews. It also enforces transfer rate limiting, handles encrypted file metadata, integrates with raftstore snapshot managers, and provides the worker runner for snapshot send/receive tasks.

## Important APIs, Types, And Functions

Constants define the protocol sizes: `PREVIEW_CHUNK_LEN` is 1 KiB, `PREVIEW_BATCH_SIZE` is 256, `FILE_CHUNK_LEN` is 1 MiB, and `USE_CACHE_THRESHOLD` is 4 MiB. `EncryptedFile` abstracts plain or decrypted file reads. `SnapCacheBuilder` lets a tablet registry build a checkpointer cache for a region; `NoSnapshotCache` disables it.

`RecvTabletSnapContext` parses the first stream message, derives `TabletSnapKey`, extracts IO type from raft snapshot data, and holds the receiving guard that prevents duplicate receives. `recv_snap_imp` implements the receive protocol; `recv_snap` wraps it in gRPC sink success/failure behavior and feeds the raft router on success. `cleanup_cache`, `is_sst_match_preview`, `accept_one_file`, and `accept_missing` handle receiver-side cache validation, file writes, checksums, and encryption key import.

On the sender side, `build_one_preview`, `find_missing`, `send_missing`, and `send_snap` implement the preview, missing-file negotiation, chunk streaming, checksum trailer, and final receiver acknowledgement. `TabletRunner<B, R>` is the `Runnable` task processor for raftstore snapshot tasks. `copy_tablet_snapshot` is a test/export helper that copies tablet snapshot files locally while preserving encryption metadata.

## Control Flow

The protocol begins with a head message containing the raft snapshot message. If sender-side SST bytes exceed the cache threshold, the sender sets `use_cache`, streams preview metadata for SST files, and waits for the receiver's missing-file list. The receiver optionally builds a cache checkpoint for the region, scans existing files, validates SST candidates by size, leading bytes, and trailing bytes, deletes stale/unmatched files, and returns the missing names. The sender streams missing SSTs plus all non-SST files in file chunks, accumulating a CRC64 digest over file names and data. It then sends an explicit end message containing the checksum, closes its sink, and waits for the receiver to close.

The receiver writes chunks into a temporary receive directory using `create_new`, validates per-file sizes, syncs each file, commits encryption metadata if present, validates the final checksum, syncs the directory, and atomically renames the temp directory to the final receive path. `RecvTabletSnapContext::finish` feeds the saved raft message into the raft router after files are persisted.

`TabletRunner::run` rejects old v1 receive tasks, bounds concurrent tablet receives and sends with counters from `TabletSnapManager`, constructs gRPC clients with current snapshot config, spawns async send/receive jobs on its internal runtime, refreshes rate-limit config on config events, and calls task callbacks with success or error.

## State And Persistence Behavior

Snapshot receive state is represented by a temporary directory and a final receive directory under `TabletSnapManager`, plus receiving/sending atomic counters. Successful receive persists snapshot files through `fs::rename`; encryption key metadata is linked before rename and cleaned after success or rename failure. Sender completion calls `finish_snapshot` through a deferred context and deletes the generated snapshot after a successful send. IO type is set with `WithIoType` so underlying filesystem accounting sees replication or load-balance work.

## Dependencies And Integration Points

This file integrates `kvproto` tablet snapshot messages, `grpcio` duplex streaming, raftstore `TabletSnapManager` and `SnapManager`, engine checkpointers through `TabletRegistry`, encryption key managers/importers, TiKV limiter and config tracker, gRPC security manager, snapshot metrics, and raft router feeding through `RaftExtension`. It consumes server `Config` fields such as concurrent snapshot limits, gRPC stream windows, keepalive, compression, and `snap_io_max_bytes_per_sec`.

## Risks And Edge Cases

The protocol is strict: unexpected message variants, chunks with repeated file names after the first chunk, size overrun, checksum mismatch, nonempty stream after end, and duplicate final paths all abort the stream. Cache reuse relies on first and last 1 KiB previews, so it is an optimization guard rather than a cryptographic identity check. Receiver-side temp directory cleanup deletes existing temp paths and encryption metadata. Encryption mismatch is fatal if a chunk carries a key but receiver encryption is disabled. `find_missing` has a TODO about Titan files and currently classifies only normal files and `.sst` names. Counters must be decremented in all async completion paths to avoid blocking future snapshot work.

## Test Signals

The visible file includes the local `copy_tablet_snapshot` helper for test/export builds. Runtime test hooks and failpoints include receive network error and finish-receiving snapshot. The task runner's validation callback path exposes current config for tests. Protocol invariants are encoded as explicit errors, which provides strong failure signals even when full integration tests live elsewhere.
