# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/Makefile

## Purpose
Builds vendored zlib 1.2.2 static/shared libraries plus `example` and `minigzip` test programs.

## Public Surface
Targets include `all`, `check`, `test`, `libz.a`, shared library target, `example`, `minigzip`, `install`, `uninstall`, `clean`, `distclean`, `tags`, and `depend`.

## Implementation Notes
- Defaults to `CC=cc`, `CFLAGS=-O`, `LIBS=libz.a`, and shared names `libz.so.1.2.2`, `libz.so.1`, `libz.so`.
- `OBJS` lists core zlib objects: checksums, deflate/inflate, trees, gz I/O, utilities.
- Optional assembler match code uses `match.S` through preprocessing.
- `test` pipes `hello world` through `minigzip` and runs `example`.
- `install` copies headers, libraries, symlinks shared names if present, and installs `zlib.3`.
- `distclean` restores `Makefile` from `Makefile.in` and `zconf.h` from `zconf.in.h`.

## Dependencies
Uses POSIX make tools, shell, `ar`, `ranlib`, optional `ldconfig`, compiler, and zlib source files.

## Risks and Notes
- Byte-identical to `Makefile.in` in this tree.
- Install/uninstall paths default to `/usr/local`.
- Filesystem relevance: build/install script only; not runtime filesystem logic.
