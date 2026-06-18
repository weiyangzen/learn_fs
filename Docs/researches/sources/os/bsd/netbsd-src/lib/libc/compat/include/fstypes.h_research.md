# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/fstypes.h

Defines old fixed-size file handle types used up through NetBSD 3.x.

It declares `struct compat_30_fid`, `struct compat_30_fhandle`, and `FHANDLE30_SIZE`.

Filesystem relevance is direct: these structures preserve old exported file-handle ABI.
