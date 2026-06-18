## sources/sync-backup/restic/internal/repository/index/index_parallel_test.go

Purpose: fixture-based tests for `ForAllIndexes`.

Important tests: `TestRepositoryForAllIndexes` loads a repository fixture, lists expected index IDs, then calls `ForAllIndexes` to ensure every index is decoded without error and reported. It then returns a sentinel callback error and asserts it propagates.

Control flow and state: expected IDs are gathered from repository listing, then compared with IDs observed through the parallel loader.

Dependencies and integration points: uses repository fixture loading, restic ID sets, and restic test helpers.

Risks and test signals: validates basic parallel loader correctness but not callback serialization under concurrent pressure or decode-error collection behavior.
