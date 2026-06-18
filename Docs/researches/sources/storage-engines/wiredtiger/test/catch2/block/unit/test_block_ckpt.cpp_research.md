<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_ckpt.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_ckpt.cpp

Purpose: Tests block checkpoint helper rounding and block modification bitstring growth.

Important APIs/types/functions: Calls `__wt_rduppo2` and `__ut_ckpt_mod_blkmod_entry`; uses `block_mods` wrapper and mock sessions.

Control flow: Rounding tests verify power-of-two alignment and invalid non-power-of-two behavior. Block-mod tests initialize empty `WT_BLOCK_MODS`, record an offset/length, and check resulting `nbits` and `bitstring` allocation.

State and persistence behavior: Local wrapper-owned `WT_BLOCK_MODS` state; no persistent files.

Dependencies and integration points: Covers checkpoint block-mod tracking, especially the WT-6366 edge that requires extra bit allocation.

Risks and test signals: Boundary at bit 256 and invalid power-of-two arguments are key. Tests should run under normal Catch2 unit target.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_ckpt.cpp -->
