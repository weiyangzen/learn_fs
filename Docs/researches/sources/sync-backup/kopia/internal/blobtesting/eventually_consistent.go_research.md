## sources/sync-backup/kopia/internal/blobtesting/eventually_consistent.go

Purpose: wraps a blob storage backend to simulate eventual consistency effects common in cloud object stores.

Important APIs/types/functions: `NewEventuallyConsistentStorage`, `eventuallyConsistentStorage`, `ecFrontendCache`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, and `shouldApplyInconsistency`.

Control flow, state, and persistence: four frontend caches randomly serve stale hits or stale not-found states for full reads. Deletes record recently deleted metadata, and listing probabilistically hides new blobs or resurrects deleted ones until `listSettleTime` elapses. Underlying storage remains the durable source; wrapper caches expire after five seconds.

Dependencies and integration points: used to test repository/provider behavior under eventual consistency. Delegates capacity, close, connection info, display, flush, and retention extension to the real storage.

Risks and test signals: probabilistic behavior can make tests flaky if assumptions are too strict. Uses `math/rand` and custom time source. No direct tests here, but provider validation can use it to exercise consistency tolerance.
