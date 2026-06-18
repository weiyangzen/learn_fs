<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_other.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_other.cpp

Purpose: Tests miscellaneous block header byte-swap helpers and sweep eligibility.

Important APIs/types/functions: Calls `__wt_block_header_byteswap_copy`, in-place byte swap through same helper, and `__wt_block_eligible_for_sweep`.

Control flow: Sections set known header values, verify little-endian no-op or big-endian swapped constants, ensure source headers remain unchanged when copying, and check local/remote object id sweep rules.

State and persistence behavior: Local `WT_BLOCK_HEADER`, `WT_BLOCK`, and `WT_BM` only.

Dependencies and integration points: Protects on-disk block header portability and tiered/local block sweep behavior.

Risks and test signals: Endianness-specific expectations must compile on both byte orders. Sweep tests signal that remote blocks are never swept and local blocks require object id not above flushed id.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_other.cpp -->
