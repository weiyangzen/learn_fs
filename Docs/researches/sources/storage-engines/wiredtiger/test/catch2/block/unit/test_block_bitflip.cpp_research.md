<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_bitflip.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_bitflip.cpp

Purpose: Tests single-bit corruption diagnosis for block checksum mismatches.

Important APIs/types/functions: `checksum_fixture` initializes `__wt_process.checksum`; tests call `__wt_checksum` and `__ut_block_bitflip_detect` with `WT_BITFLIP_MAX_SIZE` limits.

Control flow: Sections compute a correct checksum, flip one or more bits, run detection, and validate found bit positions or false results for unsupported cases.

State and persistence behavior: Local byte vectors; process-level checksum function may be initialized once.

Dependencies and integration points: Covers block read checksum diagnostic helper used for detecting likely memory corruption.

Risks and test signals: CRC collisions mean multiple-bit case only asserts non-crash. Strong signals include first/middle/last byte positions, all bit positions, size limit behavior, and data restoration after probing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_bitflip.cpp -->
