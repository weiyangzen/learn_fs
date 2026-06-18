
# sources/sync-backup/kopia/tests/repository_stress_test/repomodel/tracking_set.go

## Purpose
Implements a small generic, mutex-protected tracking set used by repository stress models to store content and manifest IDs.

## Important APIs, Types, And Functions
- `TrackingSet[T]` stores a slice of comparable IDs and a set ID for logging.
- `PickRandom` returns a random element or the zero value.
- `Snapshot` copies the current IDs into a new tracking set.
- `Replace`, `Add`, `RemoveAll`, and `Clear` mutate the stored IDs.
- `removeAll` filters a slice using `slices.Contains`.
- `NewChangeSet` creates a named tracking set.

## Control Flow
Stress tests and model code use tracking sets to pick readable/pending IDs and to publish/remove IDs during refresh/flush operations.

## State And Persistence Behavior
In-memory only. The implementation behaves like a bag rather than a strict deduplicating set: `Add` appends without checking for duplicates.

## Dependencies And Integration Points
Uses `context`, `math/rand`, `slices`, and package logger.

## Risks And Edge Cases
Because it stores a slice with no deduplication, duplicate IDs can be picked or removed together. `removeAll` is O(n*m), acceptable for stress scale but not general use. `Snapshot` copies IDs under lock, but callers inside the same package sometimes read `ids` directly from snapshot objects.

## Test Signals
Foundational support for stress-test expected state; bugs here can create false positives or false negatives.
