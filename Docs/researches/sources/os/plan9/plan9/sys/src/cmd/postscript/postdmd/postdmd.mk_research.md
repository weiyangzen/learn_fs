# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdmd/postdmd.mk

Low-level makefile for `postdmd`.

Key responsibilities:
- Defines V9 build/install variables and common compiler/linker flags.
- Builds `postdmd` from `postdmd.o`, `../common/glob.o`, `../common/misc.o`, and `../common/request.o`.
- Installs executable, `postdmd.ps` prologue, and `postdmd.1` manpage.
- Provides `clean`, `clobber`, and `changes`.

Integration:
- Delegates shared object builds to `../common/common.mk`.
- Depends on shared PostScript headers `comments.h`, `ext.h`, `gen.h`, and `path.h`.

Risks and quirks:
- Install target assumes destination directories can be created and ownership changed.
- `changes` keeps makefile and manpage install paths synchronized via simple text substitution.
