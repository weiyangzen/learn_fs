# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_page.c

Read completely: 99 lines.

This file manages btree page allocation and freeing. `__bt_free` links a page onto the tree freelist and marks metadata dirty; `__bt_new` prefers reusing the freelist head and falls back to `mpool_new`.

Important interactions: used by delete and overflow code to recycle pages, and by split/insert code to allocate new tree pages.

Security/reliability notes: freelist integrity depends on trusted page `nextpg` links. Freed pages are marked dirty so freelist state persists.
