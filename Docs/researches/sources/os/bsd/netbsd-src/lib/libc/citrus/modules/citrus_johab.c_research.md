# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_johab.c

Read completely: 395 lines.

This module implements JOHAB ctype and stdenc support for Korean encodings. It supports ASCII and two-byte Hangul, user-defined, and Hanja ranges.

Key behavior: helper predicates validate Hangul (`0x84-0xD3` lead), user-defined area (`0xD8` lead), and Hanja (`0xD9-0xDE` or `0xE0-0xF9` lead) with their allowed trail-byte ranges. `mbrtowc_priv` buffers one lead byte and completes with a validated trail byte. `wcrtomb_priv` emits ASCII or validated two-byte values. Standard encoding maps Hanja between JOHAB byte ranges and a linear 94-column index for csid 2.

Important interactions: no variables or external tables; exports through ctype/stdenc templates.

Security/reliability notes: buffer-size checks are simple and explicit. On illegal two-byte input, `mbrtowc_priv` returns `EILSEQ` without clearing `chlen`, so caller state handling after errors matters.
