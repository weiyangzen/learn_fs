# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/hcreate.c

Read completely: 243 lines.

Implements SysV/XPG4 hash table APIs: `hcreate()`, `hcreate_r()`, `hsearch()`, `hsearch_r()`, `hdestroy()`, `hdestroy_r()`, `hdestroy1()`, and `hdestroy1_r()`. A process-global table backs the non-`_r` APIs; reentrant APIs operate on caller-provided `struct hsearch_data`.

Tables are arrays of singly-linked bucket lists sized to a power of two between minimum and maximum bounds. Hashing uses NetBSD's `__default_hash`; `hsearch_r()` finds matching keys by `strcmp()`, inserts new `ENTRY` nodes for `ENTER`, and reports absent `FIND` with `*itemp = NULL` and `errno = ESRCH` while still returning success.

Destroy variants can optionally free keys and data with caller callbacks.
