# sources/sync-backup/kopia/internal/freepool/freepool.go

Purpose: wraps `sync.Pool` with typed generics and a mandatory cleanup step before objects are returned to the pool.

Important APIs/types/functions: `Pool[T]`, `Take`, `Return`, `New`, and `NewStruct`. `NewStruct` creates a pool that resets returned values to a supplied clean struct value.

Control flow: `Take` calls `sync.Pool.Get` and type-asserts to `*T`; pool `New` guarantees a pointer if callers do not insert invalid values. `Return` calls the configured cleaner before putting the object back. `New` wires the allocation and cleanup callbacks into `sync.Pool.New`.

State/persistence behavior: the pool is process-local and non-deterministic like `sync.Pool`; the runtime may drop cached values. No persistence or ordering guarantees exist.

Dependencies/integration: uses only `sync`. Intended for reusable structures that are expensive enough to benefit from pooling and can be safely reset.

Risks/test signals: `Return(nil)` or an invalid object inserted through `sync.Pool` would panic or misbehave; the API does not guard against nil. Cleanup correctness is entirely caller-provided except for `NewStruct`.
