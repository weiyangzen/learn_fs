<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/filerestorer.go -->
# sources/sync-backup/restic/internal/restorer/filerestorer.go

## Purpose
Restores regular file contents by planning blob downloads per pack and writing downloaded blobs to target files, including sparse-file and partial-overwrite support.

## Important APIs and Control Flow
`fileRestorer`, `fileInfo`, `packInfo`, `fileBlobInfo`, `newFileRestorer`, `addFile`, `restoreFiles`, `downloadPack`, `downloadBlobs`, and `reportBlobProgress` are central. `restoreFiles` maps file blobs to packs, skips matching blobs from `fileState`, tracks sparse eligibility via the zero chunk, optionally warms cold S3 packs, and launches pack download workers. `downloadPack` builds blob-to-file-offset mappings; `downloadBlobs` invokes the repository pack loader and writes every blob to every offset through `filesWriter`, using per-file locks only to ensure first create/preallocation happens once while later writes can run concurrently.

## State, Persistence, Dependencies, and Integration
State includes the pending file list, transient pack maps/order, per-file in-progress/sparse flags, and progress callbacks. It depends on repository index lookup, `LoadBlobsFromPack`, cold-storage warmup, `filesWriter`, feature flags, and restore UI progress.

## Risks and Test Signals
Risks include corrupt restores if sparse handling is wrong for partial overwrites, imprecise error attribution when pack downloads fail, and concurrency races around first file creation. Tests cover basic restore, pack skipping, repeated/frequent blobs, cold-storage warmup, download errors, and per-file error reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/filerestorer.go -->
