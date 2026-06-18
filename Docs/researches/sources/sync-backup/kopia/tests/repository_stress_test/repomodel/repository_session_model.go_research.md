
# sources/sync-backup/kopia/tests/repository_stress_test/repomodel/repository_session_model.go

## Purpose
Models a single writer session in repository stress tests, tracking pending writes and publishing them to open/shared readable sets after flush.

## Important APIs, Types, And Functions
- `RepositorySession` holds its `OpenRepo`, `WrittenContents`, and `WrittenManifests`.
- `WriteContent` and `WriteManifest` add IDs to pending session sets.
- `Refresh` delegates to the open repository to replace readable sets.
- `Flush` adds captured pending IDs to open-readable and repository-committed sets, then removes them from pending sets.

## Control Flow
Real write actions call `WriteContent`/`WriteManifest` after successful repository writes. Before flushing, stress code snapshots pending sets, flushes the real repository, then calls `Flush` with the captured sets so only definitely flushed items become visible.

## State And Persistence Behavior
In-memory expected-state transitions mirror repository flush semantics. `Flush` uses `OpenRepo.mu` to update readable and committed sets consistently.

## Dependencies And Integration Points
Uses `content.ID`, `manifest.ID`, and `TrackingSet`.

## Risks And Edge Cases
Correctness depends on capturing pending sets before real flush, because other goroutines may add more pending writes concurrently. The model intentionally does not publish writes added during the flush unless included in the captured sets.

## Test Signals
Supports validation of pending versus flushed read behavior under concurrency.
