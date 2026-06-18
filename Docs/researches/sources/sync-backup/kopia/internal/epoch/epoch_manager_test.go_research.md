# sources/sync-backup/kopia/internal/epoch/epoch_manager_test.go

Purpose: comprehensive behavioral tests for the epoch manager under normal operation, concurrency, failures, cleanup, compaction, range checkpoint generation, parameter validation, and slow-operation retries.

Important APIs/types/functions: `epochManagerTestEnv`, fake index helpers, `verifySequentialWrites`, `TestIndexEpochManager_Regular`, `Parallel`, rogue/compaction/deletion/read-only tests, slow write/refresh tests, maintenance tests, cleanup marker tests, and `forceAdvanceEpoch`.

Control flow: tests use map-backed/faulty storage with fake time, write fake JSON index shards, advance time, call refresh/maintenance methods, merge returned complete index sets, inject list/put/delete faults, and assert stats, epochs, watermarks, and retained data.

State and persistence behavior: the shared `DataMap` simulates repository blob persistence across manager instances. Tests observe blob prefixes directly and through manager snapshots.

Dependencies/integration: uses `blobtesting`, `faketime`, `fault`, `readonly`, `logging` wrappers, `errgroup`, `maintenancestats`, and `gather`.

Risks/test signals: strong coverage for protocol races, including allowed `ErrBlobNotFound` during concurrent cleanup. Some tests are nondeterministic/long and skipped under coverage or short mode. Randomness means rare failures can expose real race assumptions.
