# sources/sync-backup/restic/internal/archiver/archiver_test.go

Purpose: This is the main archiver integration/regression test file. It exercises file saving, directory and tree saving, snapshot creation, parent snapshot reuse, target resolution, filtering, error handling, metadata-only changes, cancellation, and racy filesystem changes against real test repositories and tracked filesystem wrappers.

Important APIs and helpers: `prepareTempdirRepoSrc`, `saveFile`, `blobCountingRepo`, `blobCountingSaver`, `MockFS`, `TrackFS`, `failSaveRepo`, `failSaveSaver`, `snapshot`, `overrideFS`, `overrideFile`, `mockToNoder`, and `missingFS` are test scaffolds around `New`, `Snapshot`, `runWorkers`, `save`, `saveDir`, `saveTree`, `fileChanged`, and `nodeFromFileInfo`. The benchmark functions measure small and large file chunking throughput.

Control flow and state: Tests create temporary source trees with `TestDir`, run archiver workers through `repo.WithBlobUploader`, wait on `futureNode` results, then validate repository trees with `TestEnsureFileContent`, `TestEnsureTree`, `TestEnsureSnapshot`, and `checker.TestCheckRepo`. Incremental tests track saved blob handles to ensure existing blobs and trees are not written again. Parent snapshot tests record bytes read through `MockFS` to prove unchanged files are detected from metadata and previous snapshot content instead of being reread.

Persistence and integration: The tests persist blobs into `repository.TestRepository`, `mem.New`, and wrapped backend variants. They integrate with `internal/data` tree loading, `internal/checker`, feature flags for hardlink/device metadata, `fs.Track`, `fs.NewReader`, and context cancellation. Snapshot summaries are compared against expected `Summary`, `ItemStats`, and `ChangeStats` values.

Risks and edge cases: The suite guards callback ordering, duplicate blob writes, ctime/inode ignore flags, unreadable files, missing parent paths, context-canceled snapshots, early abort when uploads fail, metadata updates without content changes, file-vs-directory races, irregular files, missing files during stat/open, explicit target filter bypass, symlink target handling, and platform differences for Windows and Darwin timestamp granularity.

Test signals: This file is itself the broadest archiver signal. It uses repository consistency checks after successful snapshots and targeted assertions for expected errors, skipped Windows/Darwin-sensitive cases, and deterministic expected tree structures.
