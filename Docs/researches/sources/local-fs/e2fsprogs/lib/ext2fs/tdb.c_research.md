# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tdb.c

This is a standalone imported Samba TDB implementation, generated from Samba common TDB sources. The header comment identifies Samba branch source `source/lib/tdb/common`, revision `23590`, dated 2007-06-22. It implements a small hash-table database with fixed on-disk records, freelist allocation, fcntl locks, optional mmap, transactions, traversal, and CRUD operations.

The on-disk format is centered on `struct tdb_header` and `struct list_struct`. A database starts with magic/version/hash metadata, a freelist head, and hash-chain heads. Each record stores next offset, total record length, key length, data length, full hash, magic, then key/data/tailer payload. Magic values distinguish live, free, dead, and recovery records.

Locking is byte-range fcntl based. It supports per-chain locks, freelist lock, global lock, transaction lock, read/write chain locks, nonblocking lock variants, and special mark-only locks. It tracks locks in `tdb_context` because POSIX locks do not nest. Traversal uses record locks to prevent deletion under iteration; if deletion collides with traversal, records can be marked dead and purged later.

I/O abstracts through `tdb_methods`, normally backed by `tdb_read`, `tdb_write`, mmap management, out-of-bounds checks, file expansion, and byte-range locks. It can fall back to `pread`/`pwrite` when mmap is unavailable or disabled. Endian conversion is supported through `TDB_CONVERT`, operating on 4-byte quantities.

Transactions intercept reads/writes by swapping the methods table to transaction-specific methods. Writes are stored in ordered transaction elements, with a mirrored hash-head table for traversal. Commit writes recovery data unless `TDB_NOSYNC` is set, upgrades locks, writes all modified regions, fsyncs/msyncs, clears recovery magic, updates mtime via `utime` where available, and then cancels the transaction state. Recovery restores old data from the recovery area and truncates the file to the old size.

Freelist management uses best-fit allocation, record splitting, tailers, and coalescing with adjacent free records. `tdb_validate_freelist` detects freelist loops by using an internal memory-only TDB as a seen set.

Public operations include open/open_ex, close, fetch, parse_record, store, append, delete, exists, firstkey/nextkey, traverse/traverse_read, lockall variants, chainlock variants, transactions, sequence-number helpers, debug dumps, freelist printing/validation, reopen/reopen_all, and flush. The default hash is a simple byte-accumulating algorithm seeded by key length.
