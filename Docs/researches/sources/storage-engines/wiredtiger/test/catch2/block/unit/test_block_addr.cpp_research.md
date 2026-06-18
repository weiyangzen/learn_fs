<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_addr.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_addr.cpp

Purpose: Unit tests for block address cookie packing and unpacking.

Important APIs/types/functions: Helpers call `__wt_block_addr_pack`, `__wt_block_addr_unpack`, and `__wt_vunpack_uint`, checking transformed offset/size/checksum values and selected hard-coded packed bytes.

Control flow: Test sections pack all-zero, zero-size, normal, manually verified, and negative-cast inputs against a `WT_BLOCK` with `allocsize=1`.

State and persistence behavior: Local `WT_BLOCK`, `WT_BM`, byte buffers, and vectors only.

Dependencies and integration points: Exercises WiredTiger variable-length integer packing and block address encoding used by block manager read/write paths.

Risks and test signals: Tests depend on internal cookie representation and tiered object id assumptions. Signals are round-trip correctness, zero-size normalization, and non-acceptance of expected bytes for negative casts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_addr.cpp -->
