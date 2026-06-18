# sources/sync-backup/kopia/snapshot/upload/upload.go

## Purpose
Implements Kopia's snapshot uploader for files and directories. It converts `fs.Entry` trees into `snapshot.Manifest` roots, writes file/symlink/directory objects through `repo.RepositoryWriter`, reuses cached objects from previous manifests, handles ignore rules and actions, records progress/statistics, and emits incomplete checkpoint snapshots during long uploads.

## Important APIs, Types, and Functions
`Uploader` is the main mutable coordinator. Public knobs include `Progress`, `MaxUploadBytes`, `ForceHashPercentage`, `ParallelUploads`, `EnableActions`, log-detail overrides, `FailFast`, `CheckpointInterval`, `DisableIgnoreRules`, and `CheckpointLabels`. `NewUploader`, `Upload`, `Cancel`, and `IsCanceled` are the public entry points. Core helpers include `uploadFileInternal`, `uploadFileData`, `uploadSymlinkInternal`, `uploadStreamingFileInternal`, `uploadDirInternal`, `processChildren`, `processDirectoryEntries`, `processSingle`, `checkpointRoot`, `periodicallyCheckpoint`, `wrapIgnorefs`, and cache helpers such as `findCachedEntry`, `metadataEquals`, and `newCachedDirEntry`. `dirReadError` preserves the distinction between root-directory read failure and child-entry failure.

## Control Flow
`Upload` starts tracing/logging/progress, validates checkpoint interval, creates a `workshare.Pool`, initializes a prototype manifest and atomic stats, then dispatches on source type. Directory uploads derive previous root directories from manifests, start background size estimation, wrap the root with `ignorefs`, execute root actions and optional OS snapshots, then call `uploadDirInternal`. `uploadDirInternal` registers a checkpoint callback, runs before/after-folder actions, handles shallow-placeholder directories, recursively processes children, writes a final directory manifest, and returns a summarized root entry. `processSingle` checks non-directory cache hits first, then handles directories, symlinks, files, `fs.ErrorEntry`, and streaming files. Regular files may be uploaded as one object or split into policy-sized parallel parts and concatenated with `repo.ConcatenateObjects`.

## State and Persistence Behavior
Persistent outputs are repository content/object blobs, directory manifests, final `snapshot.Manifest` data returned to callers, and periodic incomplete checkpoint manifests saved with `IncompleteReasonCheckpoint`. Cancellation and max-upload-byte limits set incomplete reasons rather than always failing the upload. `stats`, `totalWrittenBytes`, and cancellation flags are atomic because file work can run in parallel. Caching relies on previous snapshot entries with matching metadata and object IDs; `ForceHashPercentage` can probabilistically bypass cache. Failed entries are persisted in directory summaries via `AddFailedEntry`.

## Dependencies and Integration Points
Integrates `fs`, `ignorefs`, `snapshotfs`, `snapshot`, `policy`, `repo/object`, compression and splitter policies, OpenTelemetry tracing, content logging, `workshare`, `iocopy`, `timetrack`, OS snapshot helpers from sibling platform files, action hooks from `upload_actions.go`, progress from `upload_progress.go`, and estimation from `upload_estimator.go`.

## Risks
The code has several concurrency-sensitive areas: per-entry parallel processing updates a shared directory builder and atomic stats, file part closures capture loop indices, and checkpoints run concurrently with active writers. Error handling is policy-sensitive; root directory read failures abort while child directory failures can become fatal or ignored summary entries. Cached streaming files intentionally skip size comparison, so stable modtime/owner/mode are important. `ForceHashPercentage` uses global random state and creates nondeterministic cache behavior by design. Large-file part concatenation mutates the first part entry, so callers must not reuse part entries after concatenation.

## Test Signals
`upload_test.go` covers cache reuse, metadata compression, fail-fast and ignored error summaries, child policy on `fs.ErrorEntry`, progress callbacks, symlink stats, checkpoint manifests, parallel blob writes, large-file part concatenation, streaming files/directories, deduplication, and log-detail output. End-to-end snapshot/restore and checkpoint tests provide additional behavioral coverage.
