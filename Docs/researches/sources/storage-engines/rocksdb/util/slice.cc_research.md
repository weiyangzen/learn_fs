# sources/storage-engines/rocksdb/util/slice.cc

## Purpose

Implements built-in `SliceTransform` factories, slice transform registry creation from strings, `Slice` string/hex helpers, construction from `SliceParts`, and `PinnableSlice` move behavior.

## APIs, control flow, and state

The file defines `FixedPrefixTransform`, `CappedPrefixTransform`, and `NoopTransform`. Fixed prefix transforms require inputs at least `prefix_len_` bytes; capped transforms accept all inputs and cap output length; no-op transforms return the full source. `RegisterBuiltinSliceTransform` registers class and nickname URI patterns such as `fixed:8` and `rocksdb.CappedPrefix.8`. `SliceTransform::CreateFromString` registers once with `ObjectLibrary::Default`, parses customizable options, creates shared objects, and optionally ignores unsupported transforms. `Slice::ToString(true)` encodes bytes as uppercase hex, while `DecodeHex` validates even length and hex digits. `PinnableSlice` move assignment transfers `Cleanable` state and preserves whether the slice is pinned to external memory or self-owned string storage.

## Dependencies and integration

It depends on `rocksdb/slice.h`, `slice_transform.h`, `object_registry.h`, configurable option helpers, and `util/string_util.h`. Prefix transforms are consumed by table filters, DB options, and configuration-string parsing.

## Risks and test signals

Risks include malformed transform URI parsing, empty/zero-length prefix corner cases, hex decode validation, and ownership bugs when moving pinned slices with cleanup callbacks. `slice_transform_test.cc` covers capped-prefix behavior and DB prefix bloom integration. `slice_test.cc` covers `PinnableSlice` move and cleanup semantics, `Slice` construction from `std::string_view`, and related utility helpers.
