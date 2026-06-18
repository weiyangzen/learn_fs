# sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_impl.cc

## Purpose
This file implements RocksDB checkpoints and column-family SST export. Checkpoints create an openable point-in-time DB directory by staging live files, linking or copying them, writing replacement metadata files, and atomically renaming the staging directory into place.

## Important APIs, Types, and Functions
`Checkpoint::Create` instantiates `CheckpointImpl`. Base `Checkpoint` methods return `NotSupported` when not backed by an implementation. `CheckpointImpl::CreateCheckpoint` is the public checkpoint path. `CleanStagingDirectory` removes stale temporary files and directories. `CreateCustomCheckpoint` contains the generic live-file walking logic parameterized by link/copy/create callbacks. `ExportColumnFamily` flushes a column family, copies/links its live SSTs to an export directory, and returns `ExportImportFilesMetaData`. `ExportFilesInMetaData` iterates `ColumnFamilyMetaData` table files and handles link-to-copy fallback.

## Control Flow
`CreateCheckpoint` rejects an existing or invalid destination, derives a sibling `.tmp` staging path, cleans it, creates it, disables file deletions when supported, and calls `CreateCustomCheckpoint`. The default callbacks hard-link files into staging, copy files when links are unsupported or when `trim_to_size` is required, and create replacement files such as `CURRENT`. After copying/linking, file deletions are re-enabled, staging is renamed to the destination, and the destination directory is fsynced. Failures log and clean the staging directory.

`CreateCustomCheckpoint` records the latest sequence number, calls `GetLiveFilesStorageInfo` with WAL flush/checksum/atomic-flush options, rejects multi-directory non-WAL layouts, then processes every live file. Replacement contents are written through `create_file_cb`; otherwise files are linked first when possible and copied after `NotSupported` or when trimming is required.

`ExportColumnFamily` rejects existing or invalid export directories, creates a temporary export directory, flushes the target CF, disables file deletions, obtains CF metadata, exports table files, re-enables deletions, renames the temp dir, fsyncs it, and fills comparator and file metadata. Failure cleans whichever export directory currently owns staged files.

## State and Persistence Behavior
Checkpoint creation writes to `<checkpoint_dir>.tmp`, then renames it to the requested checkpoint path. It may hard-link SST/blob/WAL/metadata files, copy files, and create replacement metadata contents. It temporarily disables DB file deletion to keep live files stable. Export similarly writes to `<export_dir>.tmp` and returns heap-allocated metadata to the caller. Sequence number output is set only on successful checkpoint creation.

## Dependencies and Integration Points
This implementation integrates with `DB::GetLiveFilesStorageInfo`, `DisableFileDeletions`, `EnableFileDeletions`, `CopyFile`, `CreateFile`, `ParseFileName`, `ColumnFamilyMetaData`, `ExportImportFilesMetaData`, file checksum metadata, `Temperature`, and filesystem directory fsync APIs. It is used by public `rocksdb/utilities/checkpoint.h` and by backup/checkpoint tests.

## Risks and Edge Cases
`CleanStagingDirectory` deletes only direct children as files before deleting the directory, so nested unexpected contents could fail cleanup. Checkpoints and backup do not support multiple non-WAL directories (`db_paths`/CF paths). If `EnableFileDeletions` fails after a successful disable, the status is asserted in checkpoint creation but handled more softly in export. Link fallback switches to copying after `NotSupported`, but other link failures abort. Export has a FIXME around atomic flush and temperature handling. Destination paths that are empty or root-like are rejected after existence checks.

## Test Signals
`checkpoint_test.cc` covers checkpoint openability, blob files, CF export metadata, invalid paths, concurrent CURRENT changes, 2PC WAL constraints, read-only DBs, WAL locking, db_paths rejection, archived WAL handling, deletion behavior, atomic flush override paths, and backup interactions. Fault-injection tests validate durability when unsynced file data is dropped.
