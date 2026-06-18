
# sources/sync-backup/kopia/tests/repository_stress_test/repomodel/open_repository_model.go

## Purpose
Models the view of a repository opened by one logical client in repository stress tests.

## Important APIs, Types, And Functions
- `OpenRepository` stores a pointer to shared `RepositoryData`, per-open readable content/manifest sets, an `EnableMaintenance` flag, and an `openID`.
- `Refresh` replaces readable sets from committed content/manifest snapshots.
- `NewSession` creates a `RepositorySession` with per-session written content/manifest tracking sets.

## Control Flow
Stress tests call `RepositoryData.OpenRepository` before opening a real repository. Each open repository then creates sessions whose writes are tracked until flushed or refreshed.

## State And Persistence Behavior
In-memory model only. `ReadableContents` and `ReadableManifests` represent what this open repository should be able to see based on refresh/flush events.

## Dependencies And Integration Points
Uses `content.ID`, `manifest.ID`, and repository stress test logic. Logging is module-scoped via `logging.Module("repomodel")`.

## Risks And Edge Cases
`Refresh` accesses `TrackingSet.ids` directly from snapshot sets; this works within the package but assumes no concurrent mutation of those snapshot objects. Model correctness is critical because real repository errors are judged against this expected visibility model.

## Test Signals
Supports stress-test validation of repository visibility across open connections.
