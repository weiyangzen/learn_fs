# sources/test-tools/fio/oslib/strlcat.c

Purpose: fallback implementation of BSD `strlcat()`.

Important APIs/functions: `strlcat(char *dst, const char *src, size_t dsize)` appends at most `dsize - strlen(dst) - 1` bytes, NUL terminates when possible, and returns the length it tried to create.

Control flow and state: scans to the end of `dst` within `dsize`, copies from `src` while space remains, then returns `dlen + strlen(src)`.

Dependencies and integration: included only when `CONFIG_STRLCAT` is absent; paired with `strlcat.h`.

Risks: caller must pass a valid NUL-terminated `dst` within `dsize` or accept truncation semantics. This is standard `strlcat()` behavior, but misuse can still read beyond intended memory if `dst` is not terminated within `dsize`.

Test signals: exact fit, truncation, zero-size buffer, unterminated destination within size, and return-value truncation detection.
