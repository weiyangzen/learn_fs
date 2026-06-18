# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_debug.c

Read completely: 379 lines.

This file provides debug and statistics support under `DEBUG` and `STATISTICS`. It initializes a trace file, dumps tree metadata and pages, prints page entries for btree/recno internal and leaf pages, follows overflow references for display, and computes tree statistics such as levels, page counts, free space, cache hits/misses, and split counts.

Important interactions: compiled only for debug/stat builds and uses mpool page access with `MPOOL_IGNOREPIN`.

Security/reliability notes: debug output prints key/data bytes as strings in some paths, so it is not suitable for untrusted binary data diagnostics without care. Not part of normal runtime builds unless enabled.
