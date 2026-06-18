# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_conv.c

Read completely: 219 lines.

This implements btree page byte-order conversion for disk I/O. `__bt_pgin` and `__bt_pgout` swap page headers, line pointers, internal/leaf item sizes, child page numbers, and overflow references when `B_NEEDSWAP` is set; `mswap` handles the metadata page.

Important interactions: registered as mpool filters by `bt_open.c` for disk-backed trees with non-native byte order.

Security/reliability notes: conversion walks page internals based on on-page flags and offsets. Corrupt database pages could drive invalid offset interpretation unless higher layers reject them.
