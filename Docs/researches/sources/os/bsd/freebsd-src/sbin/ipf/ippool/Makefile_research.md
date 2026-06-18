# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ippool/Makefile

This FreeBSD makefile builds the `ippool` program for IPFilter lookup table management.

It sets `PACKAGE=ipf`, `PROG=ippool`, and includes generated parser/lexer sources `ippool_y.c`, `ippool_l.c`, plus `ippool.c`. It installs `ippool.5` and `ippool.8`.

The yacc and lexer generation is namespace-renamed from generic `yy` symbols to `ippool_yy` symbols via `sed`, preventing collisions with other IPFilter yacc parsers in the same toolset. It also rewrites generated lexer includes to use `ippool_y.h` and `ippool_l.h`.

`CFLAGS+= -I.` and `-Wno-error=unused-but-set-variable` reflect local generated-parser requirements.
