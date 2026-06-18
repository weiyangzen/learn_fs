
# sources/sync-backup/kopia/tests/repository_stress_test/repomodel/repository_data_model.go

## Purpose
Models repository-wide committed content and manifest IDs for repository stress tests.

## Important APIs, Types, And Functions
- `RepositoryData` holds `CommittedContents`, `CommittedManifests`, and an atomic `openCounter`.
- `OpenRepository` returns an `OpenRepository` whose readable sets snapshot the current committed sets and whose first opener receives `EnableMaintenance=true`.
- `NewRepositoryData` initializes committed tracking sets and the open counter.

## Control Flow
The stress harness creates one `RepositoryData` shared by all logical repository opens. Each real repo open obtains a model snapshot by calling `OpenRepository`.

## State And Persistence Behavior
In-memory state tracks committed IDs after modeled flushes. It does not persist to disk; persistence is in the real repository being stress-tested.

## Dependencies And Integration Points
Uses `content.ID`, `manifest.ID`, `TrackingSet`, and `sync/atomic`.

## Risks And Edge Cases
The model grants maintenance to only the first open repository using an atomic increment; if the test expects multiple maintenance-capable clients, this would under-model. Snapshot timing around open/real repo open is intentionally ordered in the stress test to avoid seeing writes that happen between model and real open.

## Test Signals
Central expected-state model for repository stress tests.
