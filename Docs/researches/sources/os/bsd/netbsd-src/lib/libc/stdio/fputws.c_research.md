# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fputws.c

Read completely: 63 lines.

This file implements `fputws`. It locks the stream, sets wide orientation, writes each wide character via `__fputwc_unlock`, and returns `-1` on the first WEOF.

Important interactions: simple loop over the wide-character output primitive.

Security/reliability notes: stops at the first NUL wide character and does not append a newline.
