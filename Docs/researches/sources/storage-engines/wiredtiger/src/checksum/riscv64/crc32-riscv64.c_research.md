<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/riscv64/crc32-riscv64.c -->
# sources/storage-engines/wiredtiger/src/checksum/riscv64/crc32-riscv64.c

## Purpose
Provides the RISC-V 64-bit architecture dispatch shim for WiredTiger CRC32C. This implementation always selects the portable software checksum routines.

## Important APIs, Types, and Functions
The exported symbols are `wiredtiger_crc32c_func(void)` and `wiredtiger_crc32c_with_seed_func(void)`, with GCC default visibility where supported. They return `__wt_checksum_sw` and `__wt_checksum_with_seed_sw`.

## Control Flow
Both exported functions are direct fallbacks. There is no runtime feature detection, hardware intrinsic use, static caching, or local checksum loop.

## State and Persistence Behavior
The file has no mutable state or direct persistence logic. Its choice of software CRC affects persisted block checksums only by routing RISC-V builds through the shared portable algorithm, preserving cross-platform checksum compatibility.

## Dependencies and Integration Points
It depends on the common WiredTiger configuration header, standard integer/size types, and software checksum symbols. It satisfies the architecture-specific checksum dispatch contract consumed by block write/read paths, tools, examples, and tests.

## Risks and Edge Cases
The primary risk is missing hardware acceleration on RISC-V platforms that may support CRC extensions. Correctness depends on the software implementation and on maintaining ABI-compatible exported function signatures. Seeded zero-length and chunked checksum behavior are inherited from `__wt_checksum_with_seed_sw`.

## Test Signals
Generic checksum tests cover this dispatch on RISC-V builds. `test_crc32.cpp` checks zero-length, known vectors, and seeded chunking, while `wt2695_checksum` compares selected checksum behavior with software over known, random, cumulative, and misaligned inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/riscv64/crc32-riscv64.c -->
