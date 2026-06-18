# File Research: sources/virtualization/qemu/block/qed-table.c

Provides QED L1/L2 table I/O. `qed_read_table()` reads a table from the image file, temporarily releases `table_lock` around block I/O, and converts little-endian disk offsets to CPU endianness. `qed_write_table()` writes a sector-aligned slice of a table, byte-swapping entries into an aligned temporary buffer and optionally flushing after the write.

The L1 wrappers read and write the fixed table at `header.l1_table_offset`. The L2 read path first drops any existing request cache reference, checks the L2 cache, allocates and reads a table on miss, commits it into the cache, and reacquires the canonical cached entry. On read failure, the untrusted loaded table is discarded.

The L2 write wrapper writes through to the image at the cached table's offset, either for a partial updated slice or a whole newly allocated L2 table. The `_sync` variants are thin wrappers around the coroutine implementations.
