# sources/storage-engines/wiredtiger/test/catch2/ext/test_key_provider_header.cpp

## Purpose
Tests the on-page crypt header format used by the key-provider/disaggregated encryption path. It verifies header layout, packing, checksum generation, validation failures, and backward/forward compatibility for v1, current, and future-sized headers.

## Important APIs, Types, And Functions
`build_crypt_page` hand-builds a `WT_CRYPT_HEADER`, byte-swaps it, copies the requested header size into a `WT_ITEM`, and writes a checksum. `kp_header_fixture` allocates a key buffer with header headroom using `__wt_buf_initsize`, exposes `kp_crypt_key_buffer`, and normalizes a copied header with `kp_copy_crypt_key_buffer`. Tests call `__ut_disagg_set_crypt_header`, `__ut_disagg_validate_crypt`, `__wt_crypt_header_byteswap`, `__wt_checksum`, and `wiredtiger_crc32c_func`.

## Control Flow
The fixture initializes a mock session and crypt key buffer. Layout tests assert structure size and offsets. Packing tests place a header before the payload and validate signature, version, compatible version, header size, crypt payload size, timestamp, total item size, and checksum. Validation tests mutate the header or item size to cover good unpack, future writer version, incompatible compatible-version, too-small item, too-small header, header bigger than buffer, and bad checksum. Compatibility tests build a 16-byte v1 header, a future version with current-compatible requirements, a longer future header, and a boundary compatible-version equal to the reader version.

## State And Persistence Behavior
State is in `WT_CRYPT_KEYS::keys` and heap-allocated unpacked headers returned by validation. The file models persisted page bytes by writing binary headers into `WT_ITEM`; no disk I/O is performed. Timestamp defaults to zero for old v1 headers that lack the appended field.

## Dependencies And Integration Points
Depends on `wt_internal.h`, Catch2, and `mock_session`. It integrates with crypt header constants such as `WT_CRYPT_HEADER_SIGNATURE`, `WT_CRYPT_HEADER_VERSION`, `WT_CRYPT_HEADER_COMPATIBLE_VERSION`, and `WT_CRYPT_HEADER_MIN_SIZE`.

## Risks And Edge Cases
The main risk is compatibility drift in the serialized header. Tests catch offset/size changes, checksum mismatches, accepting future writer versions only when compatible, rejecting pages requiring a newer reader, and preserving older v1 pages.

## Test Signals
Positive signals are zero returns from `__ut_disagg_validate_crypt` and exact unpacked field matches. Negative signals are `ENOTSUP` for incompatible reader requirements and `EIO` for malformed size/checksum cases.
