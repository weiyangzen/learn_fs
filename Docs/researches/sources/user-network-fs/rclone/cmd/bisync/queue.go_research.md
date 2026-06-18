# sources/user-network-fs/rclone/cmd/bisync/queue.go

Purpose: Captures rclone sync/copy results as structured records, executes queued file copies and resync directory copies, retries resilient transfers, syncs empty directories, and optionally saves queue files.

Important APIs/types/functions: `Results` represents one logger event side with source/destination paths, canonical name, alternate name, metadata, sigil, error, winner, side booleans, and origin. `ResultsSlice.has`, `bisyncQueueOpt`, `getHashType`, `FsPathIfAny`, `resultName`, `altName`, `WriteResults`, `ReadResults`, `preCopy`, `fastCopy`, `retryFastCopy`, `resyncDir`, `syncEmptyDirs`, `saveQueue`, and `naptime` are the core APIs.

Control flow: `preCopy` configures logger state, hash type lookup, listing metadata suppression, custom equality when needed, and slow-hash sync config. `fastCopy` saves a queue, builds a files-from filter including aliases, installs dry-run and sync logger context, stores `SyncCI` and cancel function for graceful shutdown, invokes `sync.Sync`, then decodes JSON logger results. `retryFastCopy` repeats failed syncs when `--resilient` and retry settings allow. `resyncDir` runs `sync.CopyDir` for resync. `syncEmptyDirs` explicitly mkdirs or removes directory candidates and appends synthetic `Results`.

State and persistence behavior: `WriteResults` encodes JSON into `operations.LoggerOpt.JSON`, later decoded by `ReadResults`; this in-memory log is the source for listing updates. `saveQueue` writes `<basePath>.<jobName>.que` when `SaveQueues` is true. The queue state stores `SyncCI` and `CancelSync` on `bisyncRun` for graceful shutdown.

Dependencies and integration points: Integrates with rclone `fs/sync`, `operations` logger/winner APIs, filters, accounting retry-after, hashes, terminal logging, and `bilib.Names`. Listing modification relies on the exact `Results` fields emitted here.

Risks: `WriteResults` emits one result per side per logger event, so listing code must interpret duplicates and side booleans correctly. Unknown-size files under checksum/size-only are warned because they can sync unreliably. Retry re-runs the whole queue and must reconcile prior partial results. Empty-dir synthetic results must match listing semantics.

Test signals: Golden queues/listings in copy, resync, createemptysrcdirs, rmdirs, dry_run, and resilient/volatile scenarios validate this indirectly. Focused tests should cover `ReadResults` round trip, alternate names, directory result synthesis, retry-after handling, and logger output for errors.
