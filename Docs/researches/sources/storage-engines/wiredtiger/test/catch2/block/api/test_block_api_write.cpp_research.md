<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_write.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_write.cpp

Purpose: Validates block manager `write_size`, `write`, and `read` behavior with real file I/O.

Important APIs/types/functions: `addr_cookie` stores packed addresses. `validate_block_contents` compares raw `__wt_read` data and `bm->read` data. `validate_write_block` unpacks cookies, checks checksums, flags, offset alignment, and block headers. `test_validate_cookies` rereads earlier writes.

Control flow: Tests create a block manager file, exercise size rounding, write single and multiple strings of varying sizes, validate checksummed and non-checksummed writes, and test `os_cache_dirty_max` flush behavior.

State and persistence behavior: Creates and drops `test.wt`; mutates `bm.block->fh->written`, block size, and connection read statistics.

Dependencies and integration points: Uses `setup_bm`, `create_write_buffer`, mock sessions, item wrappers, and low-level WiredTiger block/file APIs.

Risks and test signals: File-system side effects and buffer/header assumptions are the main risks. Signals include address-cookie validity, read I/O stat increments, checksum/header correctness, and cleanup after writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_write.cpp -->
