# File Research: sources/os/bsd/netbsd-src/lib/libc/string/mempcpy.c

Implements `mempcpy()` when the host/tool environment lacks it. It calls `memcpy(dst, src, len)` and returns `dst + len`.

This is a convenience wrapper with no independent overlap handling beyond `memcpy` semantics.
