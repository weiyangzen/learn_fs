# sources/sync-backup/syncthing/internal/itererr/itererr.go

Purpose: Utility helpers for Go `iter` sequences that carry their terminal error through a separate error function.

Important APIs/types/functions: `Collect` consumes an `iter.Seq[T]` into a slice and returns `errFn()`. `Zip` converts a value iterator plus error function into an `iter.Seq2[T,error]`, yielding values with nil errors and one zero-value item with the final error if non-nil. `Map` and `Map2` transform single-value sequences into new `Seq` or `Seq2` values while preserving the original iterator error and any mapping error.

Control flow: `Map`/`Map2` close over `retErr`. Iteration stops immediately when `mapFn` returns an error or when the downstream yield returns false. The returned error function gives priority to the upstream `errFn`, then returns the mapping error.

State and persistence behavior: No persistence. The only state is the captured `retErr`, so returned iterators are not designed for concurrent or repeated independent consumption.

Dependencies and integration points: Depends on the standard `iter` package. Used by code that wants idiomatic range-over-function iteration while still surfacing I/O or database scan errors after iteration.

Risks: `Zip` calls `yield` for the terminal error but does not observe that return value. `Map` and `Map2` store one shared error variable, which can surprise callers if a sequence is reused. Callers must always call the returned error function after iteration.

Test signals: No direct test in this subset. Expected coverage should include early-yield cancellation, upstream error priority, mapper errors, and successful collection.
