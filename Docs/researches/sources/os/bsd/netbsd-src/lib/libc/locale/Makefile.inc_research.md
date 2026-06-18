# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/Makefile.inc

Read completely: 75 lines.

This makefile fragment adds libc locale sources, man pages, and man-page links. It covers locale management, multibyte conversion, Unicode `uchar.h` conversion APIs, wide-character classification/translation, rune tables, and wide string numeric/collation/time functions.

It sets `.PATH` to architecture and generic locale directories, adds Citrus include paths for rune and UTF-32 conversion files, defines `WITH_RUNE`, and disables nonliteral format warnings for `wcsftime.c`.

Security/reliability notes: no runtime behavior. Build composition is important because several generated/template source files depend on compile-time include ordering and Citrus headers.
