
# sources/sync-backup/kopia/tests/robustness/engine/engine_test.go

## Purpose
Tests the robustness engine and checker over filesystem and S3 repositories, including write/snapshot/restore basics, deletion, validation failures, persistence across engine instances, weighted action selection, random action execution, IO limiting, and persisted stats/logs.

## Important APIs, Types, And Functions
- `TestEngineWriteFilesBasicFS`, `TestWriteFilesBasicS3`, and `TestDeleteSnapshotS3` cover basic write/snapshot/restore/delete behavior.
- `makeTempS3Bucket` creates a temporary AWS S3 bucket and cleanup callback using MinIO client and AWS env credentials.
- `TestSnapshotVerificationFail` swaps validation metadata to ensure restore comparison detects mismatch.
- `TestDataPersistency` persists metadata, creates a second engine on the same repos, restores old data, and compares fingerprints.
- `TestPickActionWeighted` statistically validates weighted random action selection.
- `TestActionsFilesystem` and `TestActionsS3` run random engine actions with realistic file-writer options.
- `TestIOLimitPerWriteAction` verifies file writer IO limit caps non-zero bytes written.
- `TestStatsPersist` and `TestLogsPersist` validate metadata persistence for engine stats/logs.
- `testHarness`, `newTestHarness`, `args`, `FioRunner`, and `Cleanup` encapsulate FIO writer, Kopia snapshotter, metadata persister, and engine construction.

## Control Flow
Tests set `snapmeta` mode/bucket env vars, create harnesses, initialize engines, perform writes via FIO, snapshot/restore through `Checker`, and clean up external resources. S3 tests create and remove real buckets when AWS credentials are available. Persistence tests create new persister/engine instances pointed at the same metadata repo and compare loaded state.

## State And Persistence Behavior
Creates filesystem repos under `/tmp/engine/...` or S3 paths, metadata repos, FIO data directories, persisted logs/stats/snapshot indexes, AWS buckets, and temporary local directories. `Cleanup` calls engine shutdown, FIO cleanup, server process SIGTERM when present, snapshotter/persister cleanup, and base-dir removal.

## Dependencies And Integration Points
Depends on `KOPIA_EXE`, FIO environment, AWS credentials for S3 tests, `snapmeta`, `fiofilewriter`, `kopiarunner`, `fswalker`, `minio-go`, and the engine/checker APIs.

## Risks And Edge Cases
S3 tests are external-service dependent and skip without credentials. Some global paths under `/tmp/engine` can collide if tests run concurrently outside their intended cleanup. Statistical weighted test uses 100,000 iterations and a 10 percent tolerance. `randomString` ignores `io.ReadFull` errors. Cleanup sends SIGTERM to a server process if present, which is platform/build-tag limited.

## Test Signals
Comprehensive signal for robustness engine lifecycle, persistence, random action execution, metadata/data validation, and filesystem/S3 backend support.
