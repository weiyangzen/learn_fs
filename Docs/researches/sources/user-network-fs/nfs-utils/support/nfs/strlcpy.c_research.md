# sources/user-network-fs/nfs-utils/support/nfs/strlcpy.c

Purpose: OpenBSD-compatible `strlcpy()` implementation for platforms lacking it.

Important API: `size_t strlcpy(char *dst, const char *src, size_t siz)`.

Control flow: copies up to `siz - 1` bytes, NUL-terminates if `siz != 0`, walks the rest of the source to compute and return `strlen(src)`.

State and persistence: no state.

Dependencies and integration: portability shim included in `libnfs.la`.

Risks: source and destination must not overlap unless the platform semantics permit undefined behavior. Callers must check `return >= siz` for truncation.

Test signals: zero size, one-byte buffer, exact fit, truncation, long source, and return length.
