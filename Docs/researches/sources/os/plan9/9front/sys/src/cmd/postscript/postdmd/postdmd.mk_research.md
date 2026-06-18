# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdmd/postdmd.mk

`postdmd.mk` builds and installs the DMD bitmap PostScript translator.

Build behavior:
- Uses `/bin/make`, `SYSTEM=V9`, `VERSION=3.3.2`.
- Includes `../common`.
- Header dependencies are common PostScript support headers.
- Objects are `postdmd.o` plus common `glob.o`, `misc.o`, and `request.o`.
- Installs `postdmd`, `postdmd.ps`, and `postdmd.1`.
- `changes` rewrites configurable paths/identity values and updates the manpage prologue directory string.

No runtime behavior; this is legacy build/install metadata.
