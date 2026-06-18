# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_search.c

Searches the recno btree by ordinal record number. `__rec_search` descends from root through `RINTERNAL` pages, using each internal entry's `nrecs` subtree count to find the child containing the target zero-based record number. At an `RLEAF`, it returns `t->bt_cur` with the pinned page and leaf index.

For insert and delete operations, the function increments or decrements `nrecs` in internal entries during descent and marks those pages dirty. If a later mpool lookup fails, it walks the saved parent stack and reverses the count adjustments before returning `NULL`.

Dependencies: page macros from `btree.h`, `enum SRCHOP` from `recno.h`, `BT_PUSH`/`BT_POP` stack handling, and mpool.

Risks/invariants: correctness depends on accurate internal subtree counts. The returned page is pinned and must be released by the caller.
