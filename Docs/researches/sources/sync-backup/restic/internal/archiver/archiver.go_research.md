# sources/sync-backup/restic/internal/archiver/archiver.go

## Purpose

This file implements the core archiver orchestration that turns filesystem targets into restic snapshots. It resolves backup targets, walks directory trees, applies selection filters, compares files and directories to a parent snapshot, reuses unchanged blobs when safe, delegates file and tree saving to worker pools, tracks progress/statistics, and persists a final snapshot object.

## Important APIs, Types, and Functions

- Selection/error callback types:
  - `SelectByNameFunc(item string) bool` filters by path before stat/open work.
  - `SelectFunc(item string, fi *fs.ExtendedFileInfo, fs fs.FS) bool` filters with metadata.
  - `ErrorFunc(file string, err error) error` can suppress or transform archive errors.
- Statistics:
  - `ItemStats` tracks data/tree blob counts, logical sizes, and packed repository sizes.
  - `ChangeStats` tracks new/changed/unchanged counts.
  - `Summary` records backup times, file/dir change stats, processed bytes, and aggregate item stats.
  - `(*ItemStats).Add` aggregates per-item stats.
- Interfaces:
  - `toNoder` converts filesystem metadata to `*data.Node`.
  - `archiverRepo` requires loader, async blob uploader, unpacked saver, and config access.
- `Archiver` holds repository/filesystem references, filters, options, worker savers, summary mutex/state, callbacks (`Error`, `CompleteItem`, `StartFile`, `CompleteBlob`), atime and change-detection settings.
- `Options` and `applyDefaults` set read concurrency and tree-save concurrency.
- `New` constructs an archiver with permissive default selectors and no-op callbacks.
- `error` calls the configured error handler except for context cancellation and ensures filepath context is present.
- `trackItem` invokes `CompleteItem` and updates summary counters under lock.
- `nodeFromFileInfo` converts metadata to a restic node, normalizes atime/name/device ID, and handles partial metadata errors.
- `loadSubtree` and `wrapLoadTreeError` load parent tree nodes and produce repair-oriented diagnostics.
- `saveDir`, `dirToNodeAndEntries`, `save`, `saveTree`, and `dirPathToNode` are the main recursive archive functions.
- `futureNode` and `futureNodeResult` represent asynchronous file/tree save results.
- `fileChanged` implements metadata-based change detection with optional ctime/inode ignores.
- `resolveRelativeTargets` expands targets such as `.` into their directory entries and marks explicit vs implicit targets.
- `SnapshotOptions` describes snapshot metadata and parent/skip behavior.
- `loadParentTree`, `runWorkers`, `stopWorkers`, and `Snapshot` orchestrate the complete backup.

## Control Flow

`Snapshot` initializes a summary, resolves relative targets, builds an in-memory target tree, and enters `Repo.WithBlobUploader`. Inside an errgroup worker, it starts file/tree savers, calls `saveTree` for the synthetic root with the parent tree iterator, waits for the root `futureNode`, rejects empty snapshots, records the root tree ID, and stops workers. After the uploader completes, it optionally skips snapshot creation when `SkipIfUnchanged` is set and the root tree matches the parent.

`saveTree` walks the prepared target tree in deterministic name order. Leaf nodes call `save`; interior nodes load matching parent subtrees and recurse. It passes child `futureNode`s to `treeSaver.Save`, which persists tree blobs once children resolve. `saveDir` is similar for directories discovered while walking the filesystem: read directory metadata, sorted names, use a `TreeFinder` over the previous tree, call `save` for each child, and save the resulting tree.

`save` handles one filesystem item. It resolves an absolute path, applies path-only selection before opening, opens metadata without following symlinks, stats it, applies metadata-aware selection, then branches by type. Regular files are compared with the previous node using `fileChanged`. If unchanged and all previous blobs are present in the index, it reuses previous content IDs and returns an immediate future node after refreshing metadata. If content appears missing, it warns through the error handler and stores the file again. Changed regular files are made readable, re-statted to avoid race/type-swap attacks, then handed to `fileSaver.Save`. Directories load their old subtree and call `saveDir`. Sockets are ignored. Other file types are converted to metadata-only nodes and returned immediately.

## State and Persistence Behavior

Persistent repository writes happen through `fileSaver`, `treeSaver`, the async blob uploader, and `data.SaveSnapshot`. The archiver persists data blobs for changed files, tree blobs for directory structures, and finally a snapshot file containing targets, tags, hostname, time, parent ID, root tree ID, excludes, program version, and summary. In-memory state includes worker pools, futures, parent tree iterators, callback invocations, and protected summary counters. The filesystem is read through `fs.FS`; the archiver does not intentionally mutate source files, though reading may affect atime unless disabled or filesystem behavior prevents it.

## Dependencies and Integration Points

The file integrates with many restic internals: `internal/data` for nodes/trees/snapshots, `internal/fs` for portable filesystem metadata, `internal/restic` for blob IDs/load/save/uploader interfaces, `internal/feature` for `DeviceIDForHardlinks`, `internal/debug`, and `internal/errors`. It relies on sibling archiver components such as `fileSaver`, `treeSaver`, `tree`, `backupTarget`, `pathComponents`, and `fileCompleteFunc`. Command-layer backup code configures selectors, callbacks, options, parent snapshots, and snapshot metadata.

## Risks and Edge Cases

- Race hardening is important: files are opened with `O_NOFOLLOW`, then re-statted after `MakeReadable`; if a regular file changes type, archiving is refused.
- Error handling is callback-driven. A handler can suppress errors by returning nil, which lets backup continue and may exclude problematic items.
- Unchanged-file reuse depends on both metadata comparison and index presence of all content blobs. Missing index entries force re-storage and warn that repair may be needed.
- Device ID normalization for hardlinks is gated by a feature flag to avoid unnecessary tree churn on subvolumes/snapshots.
- Relative targets with no path components are expanded to directory entries, changing explicitness and filter behavior.
- `CompleteItem` may be called from multiple goroutines; callers must be concurrency-safe.
- Empty snapshots are rejected unless the skip-if-unchanged path returns earlier.
- Parent tree load failures are reported as possible repository damage but do not always abort parent use at top level; `loadParentTree` returns nil after reporting via the error handler.

## Test Signals

Useful tests include backup/restore integration tests, parent snapshot reuse tests, changed-file detection tests with ctime/inode ignore flags, hardlink/device ID feature tests, disappearing file and type-swap race tests, exclude/filter tests, unreadable directory/file tests with error suppression, and snapshot summary assertions. Existing command integration tests in this subset exercise backup creation, no-lock restore/check, and backend load/list behavior that the archiver participates in.
