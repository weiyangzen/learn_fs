<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/crc32_wrapper.c -->
# sources/storage-engines/wiredtiger/src/checksum/power8/crc32_wrapper.c

## Purpose
Provides the POWER8 checksum dispatch wrapper. On `__powerpc64__` builds with hardware CRC enabled, it returns wrappers around the vector polynomial multiply-sum implementation; otherwise it falls back to the portable software CRC32C functions.

## Important APIs, Types, and Functions
The file declares `crc32_vpmsum(unsigned int crc, const unsigned char *p, unsigned long len)` from `vec_crc32.c`. Hardware wrappers `__checksum_hw` and `__checksum_with_seed_hw` adapt that function to WiredTiger's unseeded and seeded CRC signatures. Exported dispatch functions are `wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func`.

## Control Flow
The dispatch functions use compile-time selection only. If the build target is POWER64 and hardware CRC is not disabled, they return the vector wrappers. Otherwise they return `__wt_checksum_sw` and `__wt_checksum_with_seed_sw`. There is no runtime CPU feature probe or cached function pointer.

## State and Persistence Behavior
No mutable state exists in this wrapper. It determines which implementation produces persisted CRC32C values for block writes and validates those values on reads. Compatibility relies on `crc32_vpmsum` matching the software algorithm for all seeds and lengths.

## Dependencies and Integration Points
It depends on `wiredtiger_config.h`, the POWER8 vector implementation, and software checksum routines. It is the exported bridge between architecture-specific code in `src/checksum/power8` and the rest of WiredTiger's checksum API.

## Risks and Edge Cases
Compile-time selection assumes POWER64 builds that include this hardware path run on processors supporting the required vector crypto instructions. Unlike ARM64, there is no runtime HWCAP gate here. Signature adaptation must preserve seeded semantics, especially zero-length input returning the seed. Build configuration must exclude this path when hardware support is unavailable.

## Test Signals
`wt2695_checksum` validates the selected function against software over known vectors, random data, seeded cumulative chunks, and misalignment. `test_crc32.cpp` validates the public dispatch API and chunked seeded computation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/crc32_wrapper.c -->
