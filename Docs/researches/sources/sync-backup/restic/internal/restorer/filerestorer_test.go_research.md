<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/filerestorer_test.go -->
# sources/sync-backup/restic/internal/restorer/filerestorer_test.go

## Purpose
Unit-tests `fileRestorer` using an in-memory pack/blob repository model.

## Important APIs and Control Flow
The test scaffolding defines `TestBlob`, `TestFile`, `TestRepo`, `testPackBlob`, and `TestWarmupJob` to emulate pack layouts, blob lookup, pack loading order, and cold-storage warmup. Tests exercise basic multi-file restore, selected file restore from shared packs, very frequent blobs, loader failure, and fatal per-blob download errors. Control flow builds synthetic packs from file content, restores into temp dirs, then verifies restored bytes and warmup wait behavior.

## State, Persistence, Dependencies, and Integration
State is temporary filesystem output plus in-memory pack maps and error traces. Dependencies are `feature.S3Restore`, restic IDs/blob handles, and shared test helpers.

## Risks and Test Signals
The suite gives strong coverage of pack planning and error attribution but intentionally bypasses full snapshot traversal and metadata restoration covered in `restorer_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/filerestorer_test.go -->
