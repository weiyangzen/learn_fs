# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/Makefile

Builds `wsconsctl`, except on `octeon` where `NOPROG=yes`.

Key contents:
- Source list: `display.c`, `keyboard.c`, `keysym.c`, `map_parse.y`, `map_scan.l`, `mouse.c`, `mousecfg.c`, `util.c`, `wsconsctl.c`.
- Adds include paths for current source and build directories.
- Generates `keysym.h` from `/usr/include/dev/wscons/wsksymdef.h` using `mkkeysym.sh`.
- Declares `keysym.o` dependency on generated `keysym.h`.
- Installs `wsconsctl.8`.

Filesystem/OS relevance:
- Demonstrates OpenBSD make integration with yacc/lex sources and generated headers.
