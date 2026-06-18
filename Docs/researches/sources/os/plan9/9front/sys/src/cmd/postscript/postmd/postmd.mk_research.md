# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.mk

Build/install makefile for the `postmd` PostScript support program. It sets package defaults (`SYSTEM=V9`, `VERSION=3.3.2`, owner/group, install paths), compiles `postmd.o` plus shared objects from `../common`, links `postmd` with `-lm`, and installs the executable, `postmd.ps`, and `postmd.1`.

Integration points:
- Depends on `../common/common.mk` targets for `glob.o`, `misc.o`, `request.o`, and `tempnam.o`.
- Installs binaries under `POSTBIN` and prologue/support files under `POSTLIB`.
- `changes` rewrites this makefile and the manpage with current path/version variables using `sed`.

Risks:
- Install paths default to real system directories except `MAN1DIR=/tmp`; running `install` as root mutates system locations.
- Recursive common-object builds rely on basename target passing and local directory layout.
