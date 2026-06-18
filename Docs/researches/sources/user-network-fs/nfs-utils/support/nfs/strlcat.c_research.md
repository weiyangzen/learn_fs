# sources/user-network-fs/nfs-utils/support/nfs/strlcat.c

Purpose: OpenBSD-compatible `strlcat()` implementation for platforms lacking it.

Important API: `size_t strlcat(char *dst, const char *src, size_t siz)`.

Control flow: scans destination up to `siz`, appends source while leaving space for NUL, always NUL-terminates when there is room, and returns the length it tried to create (`initial_dst_len + strlen(src)`).

State and persistence: no state.

Dependencies and integration: included in `libnfs.la` as a portability shim through `nfslib.h`.

Risks: behavior assumes `dst` points to a valid buffer of `siz` bytes. If `dst` is not NUL-terminated within `siz`, no bytes are appended and return value signals truncation.

Test signals: normal append, exact fit, truncation, zero size, unterminated destination within size, and return-value truncation checks.
