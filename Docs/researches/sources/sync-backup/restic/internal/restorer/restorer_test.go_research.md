<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_test.go -->
# sources/sync-backup/restic/internal/restorer/restorer_test.go

## Purpose
Provides the main behavioral integration tests for snapshot restoration.

## Important APIs and Control Flow
The file defines synthetic snapshot/node builders, repository save helpers, traversal-check helpers, printer mocks, and many `TestRestorer*`/`TestRestore*` cases. It covers restoring files/dirs/special nodes, relative destinations, traversal ordering, timestamp and permission consistency, cancellation in verification, sparse files and overwrites, overwrite policies, modified-file handling, `if-changed`, dry-run, delete mode, directory overwrite behavior, restore-to-file failures, and long paths. Control flow builds test snapshots in a test repository, restores into temp dirs, mutates destinations for overwrite scenarios, and asserts filesystem state plus progress traces.

## State, Persistence, Dependencies, and Integration
State is temporary repositories/filesystems and in-memory progress/error tracking. Dependencies include `repository.TestRepository`, `internal/data`, `internal/fs`, restore UI progress, and platform helpers.

## Risks and Test Signals
This is the strongest signal for restore correctness, but it is necessarily complex and can be platform-sensitive around filesystem metadata, sparse allocation, and long path behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_test.go -->
