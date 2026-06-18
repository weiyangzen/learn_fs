# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/mbrtoc32.c

Read completely: 257 lines.

This file implements `mbrtoc32` and `mbrtoc32_l`, decoding locale multibyte input to a UTF-32 scalar value. It opens a Citrus iconv converter from the locale `CODESET` to `utf-32le`, consumes one wide character with `mbrtowc_l`, re-encodes it to multibyte from an initial state, converts that to UTF-32LE, decodes the scalar, and rejects surrogate code points.

Important interactions: bridges NetBSD's wide-character conversion with Citrus iconv and `nl_langinfo_l(CODESET)`. The private state sizing is asserted against `mbrtoc32.h`.

Security/reliability notes: `n == 0` returns incomplete without invoking iconv. Iconv open failure maps to `EIO`; conversion errors propagate. The code preserves `errno` on success. A comment says “UTF-16LE” in one conversion comment, but the code uses UTF-32LE.
