# sources/sync-backup/kopia/repo/content/indexblob/index_blob.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/indexblob/index_blob.go_research.md`.

Purpose: declares the content index blob manager interface and shared compaction option types.

Important APIs: `Manager` supports writing encrypted index blobs, listing active index blobs with a consistency timestamp, compacting active indexes, and invalidating cached manager state. `CompactOptions` controls maximum small blobs, full compaction, deleted-entry dropping, explicit content dropping, and disabling eventual-consistency safety. `DefaultIndexShardSize` sets the default maximum entries per index shard. `addBlobsToIndex` populates metadata maps without replacing existing records.

Control flow, State and persistence: this file is mostly declarations. `CompactOptions.maxEventualConsistencySettleTime` returns zero only when safety is disabled. `addBlobsToIndex` normalizes raw `blob.Metadata` into indexblob `Metadata`.

Dependencies and integration: used by `SharedManager.Refresh`, `CompactIndexes`, write-manager index flushing, and index blob manager implementations elsewhere. It bridges content indexes with maintenance statistics and blob storage.

Risks and tests: option semantics affect garbage collection and index compaction safety on eventually consistent stores. This source set indirectly tests compaction through `content_manager_test.go`; manager implementation tests live outside the listed files.
