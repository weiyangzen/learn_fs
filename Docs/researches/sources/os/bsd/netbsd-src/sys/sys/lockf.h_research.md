# File Research: sources/os/bsd/netbsd-src/sys/sys/lockf.h

Small kernel header for advisory file locking support. It forward-declares `struct lockf` and declares `lf_advlock` and `lf_init`.

Filesystem relevance is direct: vnode operations delegate POSIX/BSD advisory byte-range lock work through this API. Risks are lock state ownership through `struct lockf **`, offset handling, and vnode operation integration.
