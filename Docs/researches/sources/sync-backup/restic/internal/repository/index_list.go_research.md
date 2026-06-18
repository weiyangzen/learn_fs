## sources/sync-backup/restic/internal/repository/index_list.go

Purpose: streams blob handles directly from repository index files without building a master index.

Important APIs/types: `IndexBlob` carries either a `restic.BlobHandle` or an error. `AllIndexBlobs(ctx, lister, loader)` returns an `iter.Seq[IndexBlob]` that calls `index.ForAllIndexes`, yields each `idx.Values()` handle, supports early stop via a sentinel error, and yields loader/decode errors as `IndexBlob{Error: err}`.

Control flow and state: the iterator avoids accumulating a master index in memory. If the consumer stops early, the sentinel prevents surfacing an artificial error. Context cancellation while scanning an index is propagated through `ForAllIndexes` and yielded as an error unless it was the stop sentinel.

Dependencies and integration points: useful for commands that need a linear stream of indexed blobs. Depends on Go iterators, repository list/load interfaces, and the index package.

Risks and test signals: consumers must check `entry.Error` while iterating. Because it streams all index entries, duplicate blobs across indexes are not deduplicated here. Tests cover full streaming against a master-index baseline and early stop.
