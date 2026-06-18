# File Research: sources/os/bsd/netbsd-src/lib/libc/db/hash/Makefile.inc

Build fragment for the hash access method and ndbm compatibility layer. It adds `${.CURDIR}/db/hash` to `.PATH` and appends `hash.c`, `hash_bigkey.c`, `hash_buf.c`, `hash_func.c`, `hash_log2.c`, `hash_page.c`, `ndbmdatum.c`, and `ndbm.c` to `SRCS`.

Dependencies: used by libc's DB build along with common `db`, `mpool`, btree, and recno fragments.

Risks/invariants: source ordering is not semantically significant here, but all listed files participate in the private hash implementation contract declared in `hash/extern.h`.
