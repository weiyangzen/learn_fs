# sources/user-network-fs/samba/source3/lib/cbuf.c

Purpose: implements a talloc-owned growable character/binary buffer with a current write position and convenience formatting/quoting helpers.

Important APIs/types/functions: private `struct cbuf`; public creation/copy/delete/clear/swap/takeover/swapptr/resize/reserve/write/get/set/printf/quoted helpers.

Control flow: buffers start at 32 bytes and grow in `cbuf_reserve()` by doubling or fitting the requested space. String writes keep a debug NUL terminator, `cbuf_putdw()` writes little-endian binary data, and `cbuf_printf()` first tries available space then reserves and retries. Quoting escapes `"` and `\`, and `cbuf_print_quoted()` hex-escapes non-printable or whitespace bytes except plain space.

State and persistence: all state is in-memory under talloc; `cbuf_swap()` and `cbuf_swapptr()` adjust talloc parents to preserve ownership.

Dependencies/integration: talloc, locale `isprint/isspace`, byte-order `SIVAL`, assert, Samba `MIN/MAX/FALL_THROUGH`.

Risks/test signals: many APIs use `(size_t)-1` as sentinel despite `size_t`; `cbuf_resize()` frees the saved buffer on realloc failure, making failure destructive; several quote helpers ignore intermediate write failures. Tests should cover growth, zero/large writes, binary `putdw`, pointer swapping ownership, formatting retry, non-printable quoting, and realloc failure semantics.
