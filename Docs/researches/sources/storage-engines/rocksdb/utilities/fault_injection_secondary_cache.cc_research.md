# sources/storage-engines/rocksdb/utilities/fault_injection_secondary_cache.cc

## Purpose
This file implements `FaultInjectionSecondaryCache`, a test/stress wrapper around `SecondaryCache` that randomly injects insert and lookup failures according to a configured probability. It is used to verify RocksDB behavior when secondary cache operations fail or silently miss.

## Important APIs, types, and functions
`FaultInjectionSecondaryCache::GetErrorContext()` lazily creates a per-thread `ErrorContext` with deterministic `Random` seed via `ThreadLocalPtr`.

`Insert()` returns `Status::IOError()` when the per-thread random context hits `OneIn(prob_)`; otherwise it forwards to the base cache.

`Lookup()` has two modes. For compressed secondary cache bases, it either returns `nullptr` or directly forwards the base lookup. For other base caches, it wraps the base result handle in `ResultHandle`; when `wait` is true it can reset the handle immediately to simulate a lookup miss/failure.

`ResultHandle` defers injecting lookup failure until `IsReady()`, `Wait()`, or `WaitAll()` resolves the base handle. `UpdateHandleValue()` chooses whether to expose `Value()` and `Size()` or leave them empty.

`Erase()`, capacity APIs, printable options, and force-erase support are delegated to the base cache.

## Control flow
For asynchronous non-compressed lookups, `Lookup()` obtains a base handle and returns a wrapper. When readiness is checked, the wrapper waits or observes readiness, then calls `UpdateHandleValue()`. If the random decision does not inject failure, the wrapper captures the base value and size. In either case it resets the base handle so later calls see the wrapper's terminal state.

`WaitAll()` either filters handles before forwarding to a compressed base cache, or unwraps non-compressed handles, calls base `WaitAll()`, and updates every wrapper that still owns a base handle.

## State and persistence behavior
The wrapper has no persistent state beyond the base cache contents. Fault state is per-thread random generator state initialized from `seed_`. Wrapper result handles hold transient `value_` and `size_` after base handle completion.

## Dependencies and integration points
It depends on `rocksdb/secondary_cache.h`, `util/random.h`, and `util/thread_local.h`. Integration is through the `SecondaryCache` interface, so DB stress can install it wherever a secondary cache is configured.

## Risks and edge cases
`prob_` is passed directly to `Random::OneIn()`, so invalid zero or negative values would be unsafe unless callers validate them. The compressed-cache path does not wrap handles, which means behavior differs from other caches and failure injection occurs before wait rather than at handle completion. In non-compressed `Lookup()`, if the base returns `nullptr`, `ResultHandle::Wait()` would dereference `base_`; callers must avoid waiting on handles with no base or the wrapper must only be used in paths that honor readiness contracts.

## Test signals
No direct test file is listed for this wrapper. Expected coverage is through db_stress or secondary-cache tests configured with this wrapper.
