# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_free.c

Implementation of `acl_free()`. It calls `free()` when the supplied pointer is non-null and always returns success.

The local assignment `obj_p = NULL` has no caller-visible effect.
