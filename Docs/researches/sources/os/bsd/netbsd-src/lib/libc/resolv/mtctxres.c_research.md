# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/mtctxres.c

Implements legacy multi-thread resolver context support. With `DO_PTHREADS`, it creates a thread-specific data key for `mtctxres_t`, lazily initializes it if needed, allocates per-thread contexts, and frees them via a destructor. Without pthread support or on allocation/setup failure, it returns a shared static context.

`__res_enable_mt()` and `__res_disable_mt()` are kept as Solaris 8 private-interface compatibility stubs. The main exported accessor is `___mtctxres()`.
