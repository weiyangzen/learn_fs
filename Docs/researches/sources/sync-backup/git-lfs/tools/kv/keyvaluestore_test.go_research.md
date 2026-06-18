# sources/sync-backup/git-lfs/tools/kv/keyvaluestore_test.go

Purpose: tests persistence and optimistic merge behavior of the gob key/value store.

Important APIs/types/functions: `TestStoreSimple`, `TestStoreOptimisticConflict`, and `TestStoreReduceSize`.

Control flow: tests create temp files, mutate stores, save/reload, and compare values. The conflict test creates two store instances, saves changes from the second, then saves pending changes from the first to verify merge/replay semantics.

State and persistence: writes actual gob data to temp files and checks reload behavior and file size shrinkage after truncation.

Dependencies and integration points: uses `testify/assert`; exercises public store API plus `RegisterTypeForStorage`.

Risks: does not simulate actual simultaneous writes or corrupt files; conflict expectations document last-writer behavior for overlapping keys.

Test signals: strong coverage of normal persistence and intended optimistic conflict path.
