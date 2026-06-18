# sources/storage-engines/pebble/internal/base/value.go

Purpose: Wraps either an in-place value or a `LazyValue` in one `InternalValue` representation used by internal KVs.

APIs and types: `InternalValue`, `MakeLazyValue`, `MakeInPlaceValue`, `IsBlobValueHandle`, `IsInPlaceValue`, `InPlaceValue`, `LazyValue`, `Len`, `InternalLen`, `ValueOrHandle`, `Value`, and `Clone`.

Control flow and state: `InternalValue` stores a `LazyValue`; nil fetcher means in-place value, non-nil fetcher means lazy handle/blob. Methods enforce in-place access under invariants, delegate value fetching to `LazyValue`, and clone values/handles into caller buffers.

Persistence and dependencies: Represents values read from persisted tables or blob handles, but this wrapper is runtime-only. Depends on `errors` and `invariants`.

Integration points: Embedded in `InternalKV` and returned by iterators; used by `blobtest.ParseInternalValue` and table readers.

Risks: Calling `InPlaceValue` on a blob/lazy value panics under invariants. Ownership and cloning caveats mirror `LazyValue`.

Test signals: Covered indirectly by `lazy_value_test.go`, internal KV tests, and blob tests.
