# sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v1.go

## Purpose
Implements the v1 index-blob manager using the epoch manager rather than v0 compaction logs. V1 index handling is append-oriented and delegates active-set computation, deletion watermark advancement, and atomic multi-shard writes to `epoch.Manager`.

## Important APIs, Types, And Functions
`ManagerV1` satisfies `Manager` and exposes `ListIndexBlobInfos`, `ListActiveIndexBlobs`, `Invalidate`, `Compact`, `CompactEpoch`, `WriteIndexBlobs`, `EpochManager`, and `PrepareUpgradeToIndexBlobManagerV1`. It stores the same storage, encryption, formatting-options, and logging dependencies as v0 plus an `epoch.Manager`.

## Control Flow
Listing calls `epochMgr.GetCompleteIndexSet(epoch.LatestEpoch)` and wraps returned `blob.Metadata` as indexblob `Metadata`, also returning the deletion watermark. Normal `Compact` only advances the deletion watermark when `DropDeletedBefore` is set. `CompactEpoch` merges selected index blobs into an `index.Builder`, builds v2-capable shards, creates a random compaction session suffix, encrypts each shard under an epoch prefix, and writes them to storage. `WriteIndexBlobs` encrypts all shards first with a suffix containing shard count, then calls `epochMgr.WriteIndex` so incomplete shard sets are ignored.

## State And Persistence
Active index state and watermarks are persisted by epoch blobs managed outside this file. V1 avoids v0 `m` and `l` logs for routine operations. Upgrade preparation reads active v0 index blob IDs and writes an initial epoch under `epoch.FirstEpoch`.

## Dependencies And Integration Points
This manager depends on `epoch.Manager`, `blobcrypto`, `content/index`, `EncryptionManager`, `gather`, and format mutable parameters. It reuses `addIndexBlobsToBuilder` from the v0 implementation for reading encrypted index blobs, creating a direct integration between migration and legacy index parsing.

## Risks And Edge Cases
Atomicity depends on suffix conventions and `epochMgr.WriteIndex`; any mismatch in shard-count suffixing can make readers ignore new shards or accept partial writes. `CompactEpoch` writes directly to storage after encryption, so errors after partial writes rely on epoch completeness rules. `Compact` performs no size compaction unless deletion watermark advancement is requested.

## Test Signals
This file has no direct test in the assigned set, but v0 tests indirectly validate the shared index-reading helper. Upgrade-lock tests cover repository format upgrades that rely on epoch/v1 behavior elsewhere in the repo.
