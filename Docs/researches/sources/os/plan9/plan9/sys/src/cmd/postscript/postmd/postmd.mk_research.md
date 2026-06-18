# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.mk

Low-level makefile for `postmd`.

Key responsibilities:
- Defines build/install variables for V9, package version, ownership, directories, compiler flags, and linker flags.
- Builds `postmd` from:
  - `postmd.o`
  - `../common/glob.o`
  - `../common/misc.o`
  - `../common/request.o`
  - `../common/tempnam.o`
- Links with `-lm`.
- Installs executable, prologue `postmd.ps`, and manpage `postmd.1`.
- Provides `clean`, `clobber`, and `changes`.

Integration:
- Delegates common object builds to `../common/common.mk`, passing `SYSTEM=$(SYSTEM)` for `tempnam.o`.
- Tracks `postmd.h` and shared PostScript headers.

Risks and quirks:
- `changes` rewrites makefile variables and manpage library path using simple `sed` substitutions.
- Install target assumes ownership-changing privileges.
