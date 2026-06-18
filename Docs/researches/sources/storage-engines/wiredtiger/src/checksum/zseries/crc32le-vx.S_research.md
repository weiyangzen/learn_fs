# sources/storage-engines/wiredtiger/src/checksum/zseries/crc32le-vx.S

## Purpose
This assembly file implements the s390x Vector Extension Facility CRC32C folding kernel for little-endian, bit-reflected CRC32C. It is the performance-critical backend called by the C vector wrapper for large aligned buffers.

## Important APIs, Types, and Functions
The exported entry is `__wt_crc32c_le_vgfm_16`, created with `WT_CRC32_ENTRY`. The file defines constant blocks for IEEE CRC32 and CRC32C, but the exported WiredTiger path loads `.Lconstants_CRC_32C_LE`. Vector registers `%v9` through `%v14` hold permutation, reduction, Barrett reduction, and polynomial constants.

## Control Flow
The function preserves non-volatile registers, loads constants, places the initial CRC into a vector register, loads the first 64 bytes, permutes data from big-endian memory order into the reflected little-endian domain, and folds repeated 64-byte chunks with `VGFMAG`. It then folds four vectors to one, processes remaining 16-byte chunks, performs a final 128-bit to 32-bit fold, applies Barrett reduction, moves the final 32-bit CRC to `%r2`, restores registers, and returns.

## State and Persistence
The routine has no persistent state. It operates entirely in registers plus read-only constants. Its persistent relevance is that it must produce exactly the same checksum as the software path for on-disk and log compatibility.

## Dependencies and Integration Points
It includes `wiredtiger_config.h` and is compiled only when hardware CRC is not disabled. It uses `vx-insn.h` assembler macros to emit vector opcodes for toolchains that may not know newer mnemonics. `crc32-s390x.c` declares and calls the exported symbol through `__wt_crc32c_le_vgfm_16`.

## Risks and Edge Cases
This code is sensitive to s390x ABI register preservation, stack layout, vector instruction encoding, constants, and length preconditions. The C wrapper promises size at least 64 and 16-byte alignment for vector calls; violating that contract could lead to incorrect loads. The `.note.GNU-stack` section must remain outside conditional compilation as documented.

## Test Signals
Strong signals are s390x builds with older and newer binutils, checksum comparisons against `__wt_checksum_sw`, sanitizer or ABI checks around register preservation where available, and data-length tests around the C wrapper threshold and 16-byte remainder paths.
