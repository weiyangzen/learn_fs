# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/mod.rs

## Purpose
This file defines the row v2 module boundary, version byte, row flags, and public re-exports.

## Important APIs, Types, and Functions
`CODEC_VERSION` is `128`. The comment explains that v1 used the first byte as a datum type, so v2 starts at 128 for compatibility. Internal `Flags` has `BIG` and `WITH_CHECKSUM` bits. The module declares `compat_v1` and `row_slice`, re-exports their public APIs, and exposes `encoder_for_test`.

## Control Flow and State
There is no runtime logic beyond bitflag construction in downstream modules. The constants and flags define the byte-level contract used by `RowSlice::from_bytes` and `RowEncoder::write_row_impl`.

## Dependencies and Integration Points
The only direct dependency is `bitflags`. This module integrates row v2 decoding, v1 conversion, and test encoding under `crate::codec::row::v2`. The version and flags are shared by production row slicing and test buffer generation.

## Risks and Edge Cases
Changing `CODEC_VERSION` or flag bit assignments would break wire compatibility. `Flags` is private, which keeps external callers from depending on bit details directly, but row v2 sibling modules depend on the exact layout.

## Test Signals
There are no local tests. All `row/v2/row_slice.rs`, `compat_v1.rs`, and `encoder_for_test.rs` tests validate this module's version and flag definitions indirectly.
