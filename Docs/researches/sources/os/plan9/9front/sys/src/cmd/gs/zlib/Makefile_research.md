# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/Makefile

## Purpose
Builds the vendored zlib library and its sample programs.

## Key Elements
Defaults to `CC=cc`, `CFLAGS=-O`, static `libz.a`, and shared library names for zlib `1.2.2`. Builds objects for checksum, compression, inflate/deflate, trees, utility, and gzip I/O modules. Main targets include `all`, `test`, `libz.a`, optional shared library, `example`, `minigzip`, `install`, `uninstall`, `clean`, `distclean`, `tags`, and `depend`.

## Behavior/Risks
The default `all` target builds `example` and `minigzip`, not only the library. `test` pipes data through `minigzip` and runs `example`. Install copies headers, library, and man page into configurable prefixes. `Makefile` and `Makefile.in` are identical in this tree, so `distclean` restores this same template.

## Dependencies
Assumes a traditional Unix shell, `ar`, optional `ranlib`, compiler, and zlib source files in the same directory.
