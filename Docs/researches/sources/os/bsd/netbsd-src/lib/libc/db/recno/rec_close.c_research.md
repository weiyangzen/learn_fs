# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_close.c

Implements recno close and sync. `__rec_close` unpins any retained page, calls `__rec_sync`, unmaps mapped input if used, closes the backing record file or `FILE *`, then delegates to `__bt_close`.

`__rec_sync` has two modes. With `R_RECNOSYNC`, it only syncs the underlying btree. Otherwise, if the recno backing file is writable and modified, it imports all remaining source records, rewinds the backing file, serializes records in record-number order with either fixed-length writes or variable-length `writev` including the delimiter byte, restores the saved cursor, truncates the file to the new length, and clears `R_MODIFIED`.

Dependencies include btree sequence methods, `__bt_sync`, mpool pin handling, and recno state in `BTREE`.

Risks/invariants: sync rewrites the entire backing file. Any write/truncate failure returns error after partial output may already have occurred. Cursor restoration only restores the recno numeric cursor, not necessarily every btree cursor flag.
