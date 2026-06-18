# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_intpack.cpp

## Purpose
Tests integer packing macros and variable-length integer pack/unpack functions from WiredTiger's intpack implementation.

## Important APIs, Types, And Functions
Wrapper functions isolate return-from-macro behavior for `WT_SIZE_CHECK_PACK` and `WT_SIZE_CHECK_UNPACK`. `wt_leading_zeros_wrapper` wraps `WT_LEADING_ZEROS`. Helpers call `__wt_vpack_posint`, `__wt_vunpack_posint`, `__wt_vpack_negint`, `__wt_vunpack_negint`, `__wt_vpack_int`, and `__wt_vunpack_int`.

## Control Flow
Tests check macro constants across integer widths, bit extraction and size checks, leading-zero behavior, positive integer encodings, negative integer encodings, signed integer compact encodings for one- and two-byte ranges, and larger values including ENOMEM for insufficient buffers.

## State And Persistence Behavior
All data is in local vectors and pointers. The packed byte arrays model persisted cell/config integer encodings but are not written to disk.

## Dependencies And Integration Points
Depends on Catch2 and `wt_internal.h`. It validates low-level binary format helpers used across storage metadata and page cells.

## Risks And Edge Cases
Risks include signed/unsigned macro type surprises, buffer-size enforcement returning wrong codes, leading-zero behavior for zero and small types, and byte-order/marker regressions in variable-length encodings.

## Test Signals
Exact byte arrays, unpacked values, and error codes (`ENOMEM`, `EINVAL`) are asserted.
