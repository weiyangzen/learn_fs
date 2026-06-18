# sources/sync-backup/kopia/repo/blob/storage.go

Purpose: defines Kopia's central blob storage interfaces, sentinel errors, retention options, metadata model, and shared helper functions for listing, deletion, range validation, and metadata aggregation.

Important APIs/types/functions: interfaces include `Bytes`, `OutputBuffer`, `Volume`, `Lister`, `Reader`, and `Storage`. Data types include `Capacity`, `RetentionMode`, `PutOptions`, `ExtendOptions`, `ID`, and `Metadata`. Helpers include `ListAllBlobs`, `IterateAllPrefixesInParallel`, `EnsureLengthExactly`, `IDsFromMetadata`, `TotalLength`, `MinTimestamp`, `MaxTimestamp`, `DeleteMultiple`, `PutBlobAndGetMetadata`, and `ReadBlobMap`.

Control flow: storage implementations expose common read/list/write/delete/retention/capacity behavior. Prefix iteration fans out `ListBlobs` calls under a semaphore and returns the first callback/listing error. `DeleteMultiple` uses `errgroup` with caller-supplied parallelism. `PutBlobAndGetMetadata` ensures `GetModTime` is populated so callers receive a timestamp.

State and persistence behavior: this file stores no durable state but documents the required backend semantics: durability, read-after-write, atomic visibility, monotonic-ish timestamps, and low-latency reads. `DefaultProviderImplementation` supplies common unsupported/no-op behavior.

Dependencies/integration: every repository storage provider depends on these contracts and sentinel errors. Azure retention mode is imported for the `Locked` mode constant, and logging is used in `ReadBlobMap`.

Risks and edge cases: `IterateAllPrefixesInParallel` assumes callers make callbacks thread-safe. Passing nonpositive parallelism to `DeleteMultiple` would create a zero-capacity semaphore problem for nonempty input. `EnsureLengthExactly` treats negative expected length as full-read/no-check.

Test signals: `storage_test.go` covers listing, parallel prefix iteration, length validation, metadata helpers, parallel deletion, JSON formatting, and `PutBlobAndGetMetadata`; provider suites rely on these contracts.
