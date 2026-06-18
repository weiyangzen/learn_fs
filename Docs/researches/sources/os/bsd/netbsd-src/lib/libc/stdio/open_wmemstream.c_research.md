# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/open_wmemstream.c

Implements `open_wmemstream()` with a `funopen2()` cookie storing a wide-character buffer, size pointer, length, offset, and multibyte conversion state. Writes accept multibyte bytes from stdio, count/convert them into `wchar_t` values with `mbrlen()`/`mbrtowc()`, handle embedded NULs specially, grow the wide buffer, and update the exported size.

Seeking mirrors `open_memstream()` but resets the conversion state when the offset changes. The stream is forced wide-oriented with `fwide(fp, 1)`.
