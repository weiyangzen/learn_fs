# File Research: sources/os/bsd/openbsd-src/sbin/savecore/Makefile

This Makefile builds the OpenBSD `savecore` utility.

Key settings:
- `PROG=savecore`
- `SRCS=savecore.c zopen.c`
- Links with `-lkvm` through `LDADD` and `${LIBKVM}` through `DPADD`.
- Installs `savecore.8`.

Integration:
- `savecore.c` uses libkvm for dump metadata/header handling.
- `zopen.c` provides built-in `.Z` compression support.

Risk notes:
- Compression support is compiled directly into the utility rather than using an external compressor.
