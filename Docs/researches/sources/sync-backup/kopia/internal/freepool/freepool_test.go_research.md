# sources/sync-backup/kopia/internal/freepool/freepool_test.go

Purpose: validates typed object pooling, cleanup-on-return, and basic reuse behavior.

Important APIs/types/functions: `freepool.NewStruct`, `freepool.New`, `Pool.Take`, and `Pool.Return`. The tests use integer and simple struct values.

Control flow: `TestNewStruct` takes a clean struct, mutates it, returns it, and expects the next taken value to be reset. `TestNew` performs the same pattern with explicit maker and cleaner callbacks. `TestPool_MultipleItems` checks that two simultaneously checked-out items are distinct before and after return.

State/persistence behavior: no persistent state. The tests assume immediate reuse from `sync.Pool`, which usually holds within one test but is not a strict long-term guarantee across GC boundaries.

Dependencies/integration: exercises only exported freepool APIs. There are no concurrency tests.

Risks/test signals: the tests do not cover nil returns, panic behavior, or runtime pool eviction. They do catch accidental removal of cleanup or typed allocation.
