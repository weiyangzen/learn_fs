# sources/sync-backup/git-lfs/locking/cache_test.go

Purpose: Tests lock cache add/list/remove behavior.

Important APIs/types/functions: Exercises `NewLockCache`, `Add`, `Locks`, `RemoveByPath`, and `RemoveById`.

Control flow: Creates a temp cache file, adds three locks, asserts listed locks, removes one by path, asserts remaining locks, removes another by id, and asserts final state.

State and persistence behavior: Uses a temporary store file but does not call `Save`; the tested behavior is in-memory store mutation.

Dependencies and integration points: Depends on `Lock` equality through testify `Contains` and `kv.Store` behavior.

Risks and edge cases: Does not test persistence reload, clear, id key encoding idempotence, or store corruption.

Test signals: Basic correctness signal for bidirectional removal.
