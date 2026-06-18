<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/uploader.go -->
# sources/sync-backup/git-lfs/commands/uploader.go

## Research

`uploader.go` coordinates push-time LFS uploads. `uploadForRefUpdates` verifies locks, computes remote SHAs to exclude, creates a transfer queue per ref update, scans either all reachable objects or multi-range differences, collects transfer errors, and reports deferred errors. `uploadContext` owns remote selection, transfer manifest, dry-run behavior, uploaded-OID deduplication, progress logger/meter, lock verifier, committer identity, and maps for missing/corrupt objects.

Key APIs are `newUploadContext`, `NewQueue`, `buildGitScanner`, `gitScannerCallback`, `prepareUpload`, `UploadPointers`, `CollectErrors`, `ReportErrors`, `uploadTransfer`, `supportsLockingAPI`, and `disableFor`. Control flow moves from GitScanner callbacks to `prepareUpload`, then to `tq.TransferQueue.Add`; missing local media files are either marked as malformed or allowed by `lfs.allowincompletepush`. Persistent effects are local object reads, stdout progress, process-exit decisions, and `cfg.SetGitLocalKey` when disabling lock verification. Dependencies include `git`, `lfs`, `tq`, `tasklog`, lock verification, config, and `tracerx`. Risks include duplicate scanner results, lock-verification policy differences, dry-run deduplication, exit-code behavior, missing/corrupt upload handling, and hard-coded known locking hosts. `uploader_test.go` covers locking host URL matching.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/uploader.go -->
