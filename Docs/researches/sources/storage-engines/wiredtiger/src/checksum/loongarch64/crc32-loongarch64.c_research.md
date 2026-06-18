<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/loongarch64/crc32-loongarch64.c -->
# sources/storage-engines/wiredtiger/src/checksum/loongarch64/crc32-loongarch64.c

## Purpose
Provides the LoongArch64 architecture dispatch shim for WiredTiger CRC32C. In this implementation it always selects the portable software checksum routines.

## Important APIs, Types, and Functions
The exported symbols are `wiredtiger_crc32c_func(void)` and `wiredtiger_crc32c_with_seed_func(void)`, with GCC default visibility when available. They return external software implementations `__wt_checksum_sw` and `__wt_checksum_with_seed_sw`.

## Control Flow
Both dispatch functions are direct returns with no runtime feature checks, static cache, allocation, or architecture-specific computation. The unseeded API returns the software function accepting `(const void *, size_t)`. The seeded API returns the software function accepting `(uint32_t, const void *, size_t)`.

## State and Persistence Behavior
This file has no mutable state. Its persisted-data impact is indirect: LoongArch64 builds produce and validate WiredTiger CRC32C values through the common software implementation, preserving on-disk checksum compatibility with other architectures.

## Dependencies and Integration Points
It depends on `wiredtiger_config.h`, integer and size types, and the software checksum object. It satisfies the same exported checksum dispatch contract used by block manager writes/reads, recovery verification, tools, examples, and checksum tests.

## Risks and Edge Cases
The main risk is performance, not correctness: hardware support is not used even if a LoongArch64 platform exposes CRC acceleration. ABI compatibility depends on the exported function signatures and visibility matching other architecture shims. Any change to software seeded semantics must remain compatible with this dispatch file.

## Test Signals
The generic CRC tests exercise this path on LoongArch64: `test_crc32.cpp` checks zero-length, known-value, and chunked seeded behavior, while `wt2695_checksum` compares the selected checksum path with the software implementation across random data and misalignment cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/loongarch64/crc32-loongarch64.c -->
