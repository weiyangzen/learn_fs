# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_fileio.c

Thin file I/O wrappers for vector I/O.

`isns_file_writev` calls either `wepe_sys_writev` when `HAVE_WEPE` is enabled or plain `writev`. `isns_file_readv` does the same for read side with `readv`.

These wrappers isolate platform-specific WEPE support from the rest of `libisns`.
