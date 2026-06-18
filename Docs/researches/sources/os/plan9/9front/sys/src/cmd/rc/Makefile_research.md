# File Research: sources/os/plan9/9front/sys/src/cmd/rc/Makefile

This Makefile builds the Unix-hosted `rc` shell target.

Key contents:
- Target binary: `rc`.
- Object files include parser/runtime modules such as `code.o`, `exec.o`, `glob.o`, `lex.o`, `pcmd.o`, `pfnc.o`, `simple.o`, `tree.o`, `var.o`, `unix.o`, and generated parser object `syn.o`.
- Header dependencies include `rc.h`, `y.tab.h`, `io.h`, `exec.h`, `fns.h`, and `getflags.h`.
- Grammar source: `syn.y`, built with `YFLAGS=-d`.
- `PREFIX` defaults to `/usr/local`.
- `install` copies `rc` to `$(PREFIX)/bin/` and `rcmain.unix` to `$(PREFIX)/lib/rcmain`.
- `unix.o` is compiled with `-DPREFIX="$(PREFIX)"`.
- `clean` removes objects, binary, and generated parser files.

Implementation notes:
- This is a conventional portable makefile rather than a Plan 9 `mkfile`.
- `y.tab.h` depends on generated `syn.c`.
