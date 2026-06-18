# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/kmem.h

Header for the kernel-memory helper API.

Key contents:
- Declares `openkmem()`, `kmemcpy()`, and `kstrncpy()`.
- Defines `KMEM` from `_PATH_KMEM` when available, otherwise `/dev/kmem`.
- Includes NetBSD path handling when compiled there.

Research notes:
- Legacy `__P` compatibility macro remains present.
