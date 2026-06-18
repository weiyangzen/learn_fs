## sources/sync-backup/kopia/internal/blobtesting/object_locking_map_test.go

Purpose: smoke test for versioned object-locking map storage.

Important APIs/types/functions: `TestObjectLockingStorage`.

Control flow, state, and persistence: constructs `NewVersionedMapStorage` and runs the generic storage verifier with governance retention options.

Dependencies and integration points: validates the object-locking fake through the same contract as other blob storages.

Risks and test signals: broad smoke coverage only; retention-specific edge cases such as locked delete/touch semantics need targeted tests elsewhere.
