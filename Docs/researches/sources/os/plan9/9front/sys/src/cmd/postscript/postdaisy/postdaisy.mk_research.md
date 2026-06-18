# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.mk

`postdaisy.mk` builds and installs the Diablo 1640 PostScript translator.

Build behavior:
- Uses `/bin/make`, `SYSTEM=V9`, `VERSION=3.3.2`.
- Compiles with `-O` and includes `../common`.
- Headers include `postdaisy.h` and shared common headers.
- Objects are `postdaisy.o` plus common `glob.o`, `misc.o`, and `request.o`.
- Links `postdaisy` without extra libraries.
- Installs executable, `postdaisy.ps`, and `postdaisy.1` to configurable directories with ownership/permissions.
- `changes` rewrites configuration variables and updates the prologue directory reference in the manpage.

This is a preserved portable makefile separate from the directory’s Plan 9 `mkfile`.
