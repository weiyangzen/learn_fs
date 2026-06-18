# sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v0.go

## Purpose
Implements the legacy v0 index-blob manager. It stores active index shards under `n`, compaction logs under `m`, and delayed cleanup records under `l`, then reconstructs the active index set by subtracting compacted inputs only when all compaction outputs are visible. The file is primarily about making index compaction work on eventually consistent blob stores without resurrecting old or deleted content entries.

## Important APIs, Types, And Functions
`ManagerV0` satisfies `indexblob.Manager` with `ListIndexBlobInfos`, `ListActiveIndexBlobs`, `Compact`, `WriteIndexBlobs`, and `Invalidate`. `compactionLogEntry` persists input/output `blob.Metadata` for compactions; `cleanupEntry` persists delayed deletion targets and schedule time. `IndexFormattingOptions` is the dependency boundary to format mutable parameters. Internal helpers include `registerCompaction`, `deleteOldBlobs`, `cleanup`, `getBlobsToCompact`, `compactIndexBlobs`, `dropContentsFromBuilder`, `addIndexBlobsToBuilder`, and `removeCompactedIndexes`.

## Control Flow
Listing runs two storage scans in parallel for `m` and `n` blobs, loads compaction entries, and removes compacted inputs only for logs whose outputs are present. Compaction lists active blobs, reads mutable parameters for pack/index sizing, selects candidates, builds a merged `index.Builder`, optionally drops deleted/manual content entries, writes replacement index blobs, registers the compaction, and then performs cleanup. Cleanup happens in stages: old input `n` blobs are deleted only after the compaction log is old enough, then old compaction logs are written into cleanup `l` markers, and only later are `m` and `l` blobs deleted.

## State And Persistence
Persistent state is entirely in blob storage: encrypted index blobs, encrypted JSON compaction logs, and encrypted JSON cleanup markers. `ListActiveIndexBlobs` returns a zero deletion watermark for v0. `timeNow` is injected but deletion decisions rely on server blob timestamps from storage metadata to tolerate client clock drift. Storage cache flushing is attempted after cleanup.

## Dependencies And Integration Points
The manager depends on `blob.Storage`, `EncryptionManager`, `content/index`, `format.MutableParameters`, `maintenancestats`, `gather`, and structured content logging. It is used by content managers that need v0 index discovery and by upgrade code that migrates legacy indexes into epoch-managed v1 indexes.

## Risks And Edge Cases
The critical correctness risk is deleting compaction logs before old index blobs, which can resurrect superseded indexes; this file explicitly deletes index blobs first. Another risk is compacting deleted entries too early or with incomplete compaction output visibility. Corrupt or unreadable compaction/cleanup blobs fail listing/cleanup, while missing blobs during reads are tolerated as concurrent deletion. Candidate selection depends on `MaxPackSize` and `CompactOptions`, so misconfigured mutable parameters can make compaction ineffective or too aggressive.

## Test Signals
`index_blob_manager_v0_test.go` stress-tests concurrent writing, reading, deletion, undelete, compaction, eventual consistency delays, and resurrection prevention. It also checks expected counts of `n`, `m`, and `l` blobs after delayed cleanup.
