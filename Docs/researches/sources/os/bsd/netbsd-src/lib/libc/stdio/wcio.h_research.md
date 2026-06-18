# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wcio.h

Read completely: 70 lines.

Internal wide-character I/O support header. It defines `struct wchar_io_data`, holding input/output `mbstate_t`, a minimal one-character `ungetwc` buffer, unget count, and stream orientation mode.

Macros provide access and lifecycle operations: `WCIO_GET(fp)`, `WCIO_FREE(fp)`, `WCIO_FREEUB(fp)`, and `_SET_ORIENTATION(fp, mode)`. This header coordinates wide/multibyte conversion state stored in the extended `FILE` structure.
