# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_close.c

Read completely: 181 lines.

This implements btree close and sync. `__bt_close` unpins any cached page, syncs, closes the mpool, frees cursor/result buffers and tree/DB structures, then closes the file descriptor. `__bt_sync` writes metadata if dirty, syncs mpool pages, and clears `B_MODIFIED`; `bt_meta` writes the metadata page fields.

Important interactions: uses mpool for page caching and the `B_MODIFIED`/`B_METADIRTY` flags to decide what must reach disk.

Security/reliability notes: close returns early on sync/mpool errors and may leave ownership with the caller. Metadata writes are raw structure copies into page zero.
