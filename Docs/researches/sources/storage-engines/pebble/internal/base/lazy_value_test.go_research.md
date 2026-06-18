# sources/storage-engines/pebble/internal/base/lazy_value_test.go

Purpose: Tests `LazyValue` in-place and lazy-fetch behavior.

APIs and types: Uses a `valueFetcherFunc` implementation and exercises `LazyValue.Value`, `Len`, `TryGetShortAttribute`, and `Clone`.

Control flow and state: Test cases cover raw in-place values, lazy handles with fetch metadata, caller-owned buffers, and cloned lazy values using caller-provided fetcher storage.

Persistence and dependencies: No persistence. Fetching is simulated by the test function.

Integration points: Protects the value contract relied on by iterators and blob/value-block readers.

Risks: Does not exercise real blob readers or iterator repositioning lifetimes; those are integration concerns.

Test signals: Good focused coverage for ownership flags and metadata propagation.
