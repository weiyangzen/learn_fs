# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postbgi/postbgi.mk

`postbgi.mk` is the historical Unix makefile for building and installing `postbgi`.

Build behavior:
- Uses `/bin/make`, `SYSTEM=V9`, `VERSION=3.3.2`, owner/group `bin`.
- Installs binaries under `/usr/bin/postscript`, prologue under `/usr/lib/postscript`, and manpage under `/tmp` by default.
- Includes common headers from `../common`.
- Builds `postbgi.o` plus common objects `glob.o`, `misc.o`, and `request.o`.
- Links with `-lm` because `postbgi.c` uses math functions such as `atan2`.
- Delegates common object builds to `../common/common.mk`.
- `changes` rewrites configurable make variables and updates the `.ds dQ` path in `postbgi.1`.

This is not the native Plan 9 `mkfile`; it is a preserved portable makefile.
