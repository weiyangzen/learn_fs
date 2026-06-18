# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.mk

Low-level makefile for building and installing `postdaisy`.

Key responsibilities:
- Defines build/install variables: `SYSTEM=V9`, `VERSION=3.3.2`, owner/group, manpage directory, PostScript binary directory, library directory, common directory, compiler flags, and linker flags.
- Builds `postdaisy` from:
  - `postdaisy.o`
  - `../common/glob.o`
  - `../common/misc.o`
  - `../common/request.o`
- Tracks headers `postdaisy.h`, `comments.h`, `ext.h`, `gen.h`, and `path.h`.
- Installs executable, prologue `postdaisy.ps`, and manpage `postdaisy.1`.
- Provides `clean`, `clobber`, and `changes` targets.

Integration:
- Common object targets delegate into `../common` with `common.mk`.
- `changes` rewrites selected makefile variables and the manpage `.ds dQ` PostScript library path.

Risks and quirks:
- Uses historical `chgrp`/`chown` install steps that assume privileged installation.
- The `changes` target edits files through temporary `XXX.*` names and simple `sed` substitutions.
- Does not include `Opostdaisy.c`; the built program is `postdaisy.c`.
