# sources/storage-engines/pebble/internal/base/lazy_value.go

Purpose: Represents values that may be in-place or lazily fetched from a value block/blob, with optional short attributes and value length metadata.

APIs and types: `ShortAttribute`, `MaxShortAttribute`, `ShortAttributeExtractor`, `AttributeAndLen`, `LazyValue`, `LazyFetcher`, `ValueFetcher`, `LazyValue.Value`, `Len`, `TryGetShortAttribute`, `Clone`, `NoBlobFetches`, and `errValueFetcher`.

Control flow and state: If `LazyValue.Fetcher` is nil, `ValueOrHandle` is the value. Otherwise it is a handle passed to `ValueFetcher.FetchHandle` with blob file ID and expected length. `Clone` copies handle/value bytes into a caller buffer and copies fetcher metadata into caller-provided storage without fetching.

Persistence and dependencies: No direct persistence, but handles and attributes correspond to values stored outside the key in value blocks or blob files. Depends on `context` and base blob ID types.

Integration points: Returned by `InternalIterator` and wrapped by `InternalValue`. Sstable/blob readers implement `ValueFetcher`; `blobtest.Values` provides test fetchers.

Risks: Memory ownership is subtle: iterator-owned value memory is unstable after repositioning, and cloned lazy values may refetch. The current `Value` call uses `context.TODO`, so cancellation must be handled at higher layers or by future API changes. `NoBlobFetches` is intended to catch unexpected blob access.

Test signals: `lazy_value_test.go` verifies in-place/lazy value retrieval, length, attribute, cloning, and fetcher behavior.
