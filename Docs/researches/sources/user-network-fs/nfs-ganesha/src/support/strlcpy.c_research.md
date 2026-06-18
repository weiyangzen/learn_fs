# sources/user-network-fs/nfs-ganesha/src/support/strlcpy.c

Purpose: compatibility implementation of BSD `strlcpy` when the platform lacks `HAVE_STRLCPY`.

Important APIs, types, and functions: exports `size_t strlcpy(char *dst, const char *src, size_t siz)` under the feature guard. It copies up to `siz - 1` bytes, NUL-terminates when `siz != 0`, and returns the full source length.

Control flow: it copies while space remains, stops early on source NUL, otherwise writes a terminating NUL and advances through the rest of `src` to compute the return value.

State and persistence: no persistent state; pure buffer utility.

Dependencies and integration points: depends only on `<sys/types.h>` and build-time feature detection. It provides the expected libc-like symbol for the rest of the tree.

Risks: like standard `strlcpy`, behavior is undefined for invalid pointers or overlapping buffers. Return value must be checked by callers to detect truncation.

Test signals: unit tests should cover `siz == 0`, exact fit, truncation, empty source, and return length.
