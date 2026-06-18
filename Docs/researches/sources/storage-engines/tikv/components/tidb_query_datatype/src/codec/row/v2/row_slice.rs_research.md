# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/row_slice.rs

## Purpose
This file implements zero-copy decoding and lookup for TiDB/TiKV row-format-v2 byte slices. It parses the row header, ID arrays, offset arrays, value region, and optional checksum without materializing per-column values.

## Important APIs, Types, and Functions
`RowSlice<'a>` has `Small` and `Big` variants. Small rows store non-null IDs and null IDs as `u8` and offsets as `u16`; big rows store IDs and offsets as `u32`. Both variants retain the original bytes, the values slice, and optional `Checksum`. `RowSlice::from_bytes` parses a row, `search_in_non_null_ids` binary-searches sorted non-null IDs and returns a value byte range, `search_in_null_ids` checks null IDs, `get` returns an optional value slice for a column, `values` and `origin` expose raw slices, and `get_checksum` returns parsed checksum metadata.

`Checksum` stores a header, primary crc32 value, and optional extra checksum value. `LeBytes<'a, T>` is a little-endian unaligned view over integer arrays with `get`, `get_unchecked`, and a bounded `binary_search`.

## Control Flow and State
`from_bytes` asserts the first byte is `CODEC_VERSION`, reads flags, counts, and typed little-endian arrays. If `WITH_CHECKSUM` is set, it calls `cut_checksum_bytes` using the last non-null offset to split trailing checksum bytes away from the values region, then parses a 5-byte or 9-byte checksum trailer. Lookups validate the requested column ID against the row width, binary-search the appropriate ID array, derive the start offset from the previous offset or zero, and return a slice from `values`.

## Dependencies and Integration Points
The module depends on `codec::prelude` for reading primitives, `num_traits::PrimInt` for generic little-endian arrays, local codec errors, and row v2 constants/flags. It integrates with `encoder_for_test` for test fixtures and with higher-level datum decoders that consume the returned raw value payload.

## Risks and Edge Cases
The implementation is only compiled for little-endian targets. `from_bytes` uses `assert_eq!` for the version byte and checksum length assertions, so malformed data can panic instead of returning a codec error. `cut_checksum_bytes` unwraps the last offset when checksum is present and non-null count is nonzero, so corrupted offset arrays can also panic. The custom binary search limits steps to 20 to avoid pathological corrupted rows, but it still relies on sorted ID arrays from the encoder/TiDB contract. `LeBytes` uses unaligned unsafe reads; bounds are checked in safe `get`, while internal search uses calculated indices.

## Test Signals
Tests cover little-endian array reading, big and small non-null lookup, null lookup with IDs inside and outside width ranges, checksum decoding with and without extra checksum for both small and big rows, and benchmarks for lookup and parsing performance.
