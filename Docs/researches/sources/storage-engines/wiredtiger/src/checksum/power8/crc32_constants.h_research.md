<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/crc32_constants.h -->
# sources/storage-engines/wiredtiger/src/checksum/power8/crc32_constants.h

## Purpose
Contains generated constants for the POWER8 vector CRC32C implementation. The file is generated from the `crc32-vpmsum` tooling for reflected CRC32C polynomial `0x1edc6f41` with final XOR enabled and a maximum folding block size of 32768 bytes.

## Important APIs, Types, and Functions
This header defines `CRC`, `CRC_XOR`, `REFLECT`, and `MAX_SIZE`. Under `CRC_TABLE`, it provides `crc_table[]` for byte-at-a-time alignment and tail handling. Under `POWER8_INTRINSICS`, it provides aligned vector tables `vcrc_const[255]` for large-block folding, `vcrc_short_const[16]` for short and tail reductions, and `v_Barrett_const[2]` for final Barrett reduction. The vector tables have endian-specific lane ordering.

## Control Flow
There is no executable control flow. Consumers compile in different constant sets via `CRC_TABLE` and `POWER8_INTRINSICS`. `vec_crc32.c` defines both before including this header, using `crc_table` in `crc32_align`, the long and short vector constants in `__crc32_vpmsum`, and `v_Barrett_const` during final polynomial reduction.

## State and Persistence Behavior
All data is static constant state. The constants define the actual CRC32C polynomial arithmetic used to persist and verify block checksums on POWER8 hardware builds. They must remain bit-for-bit compatible with software CRC32C and other architecture implementations.

## Dependencies and Integration Points
The header is private to the POWER8 checksum implementation and assumes AltiVec vector types when `POWER8_INTRINSICS` is defined. It integrates with `vec_crc32.c` and, through `crc32_wrapper.c`, with the exported WiredTiger checksum dispatch API.

## Risks and Edge Cases
The file explicitly says it is generated and should not be edited manually. Risks include accidental table corruption, regenerating with the wrong polynomial/reflection/XOR settings, or breaking endian-specific ordering. Because checksum values are persisted in block headers and address cookies, a constants mismatch is a data-compatibility bug rather than a local performance issue.

## Test Signals
The strongest validation is cross-checking this POWER8 path against `__wt_checksum_sw` in `wt2695_checksum`, including known CRC32C vectors, seeded cumulative checksums, random data, and misalignment. `test_crc32.cpp` also verifies known values and chunked seeded behavior through the public dispatch API.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/crc32_constants.h -->
