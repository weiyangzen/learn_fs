# File Research: sources/os/bsd/netbsd-src/lib/libc/nls/catclose.c

Implementation of `_catclose()`. It rejects `(nl_catd)-1` with `EBADF`; for non-null descriptors it unmaps the mapped catalog data using the stored size and frees the descriptor object.

A null catalog descriptor is accepted and returns success without doing work.
