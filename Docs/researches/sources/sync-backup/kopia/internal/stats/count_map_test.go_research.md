<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/count_map_test.go -->
# sources/sync-backup/kopia/internal/stats/count_map_test.go

- Purpose: Tests `CountersMap` behavior and concurrency.
- Important APIs/types/functions: `TestConcurrentCountMap_Get_MissingKey`, `TestConcurrentCountMap_IncrementAndGet_NewAndExistingKey`, `TestConcurrentCountMap_Add`, `TestConcurrentCountMap_Range`, `TestConcurrentCountMap_Length`, `TestConcurrentCountMap_Range_StopEarly`, `TestConcurrentCountMap_CountMap_Snapshot`, `TestConcurrentCountMap_ConcurrentIncrement`.
- Control flow: Tests instantiate maps with string/int keys, perform adds/increments, inspect values and length, stop iteration early, and run multiple goroutines incrementing one key.
- State and persistence: In-memory atomic counters only.
- Dependencies and integration points: Uses `sync`, `testing`, and `testify/require`.
- Risks and edge cases: Tests do not cover overflow or heavily contended new-key creation beyond one shared key.
- Test signals: Direct coverage for `count_map.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/count_map_test.go -->
