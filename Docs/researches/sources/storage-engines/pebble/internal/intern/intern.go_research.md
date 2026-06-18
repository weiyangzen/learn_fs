# sources/storage-engines/pebble/internal/intern/intern.go

## Purpose
`intern.go` provides a tiny byte-slice-to-string interning helper intended to avoid repeated allocations for repeated byte content.

## Important APIs, Types, And Functions
Package-level `pool` is a `sync.Pool` of `map[string]string`. `Bytes(b []byte) string` looks up the string content in a pooled map, returns the existing interned string if present, otherwise allocates a string, stores it as both key and value, and returns it.

## Control Flow
`Bytes` gets one map from the pool, performs lookup by `string(b)`, puts the map back before returning, and either reuses an existing canonical string or stores a new one.

## State And Persistence Behavior
Intern maps live in `sync.Pool`, so state is process-local and opportunistically retained; GC may drop pool entries. Interning is not global or durable and may return different backing strings after pool churn.

## Dependencies And Integration Points
It depends only on `sync`. It is useful in paths repeatedly converting equal byte slices to strings where a pooled map can amortize allocations.

## Risks And Edge Cases
The `string(b)` lookup conversion can allocate if the key is absent; the optimization relies on compiler/runtime behavior and pooled map reuse. Under the race detector `sync.Pool` behavior changes enough that allocation tests skip. The maps can grow over time while retained in the pool.

## Test Signals
`intern_test.go` checks zero allocations for repeated `abc` slices outside race builds.
