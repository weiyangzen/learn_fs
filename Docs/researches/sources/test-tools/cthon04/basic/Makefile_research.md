# sources/test-tools/cthon04/basic/Makefile

Purpose: Makefile for the Connectathon basic test programs. It builds original tests `test1` through `test9`, auxiliary tests, lint targets, copy targets, and source distribution artifacts.

Important APIs/types/functions: variables `TESTS`, `AUXTESTS`, `DOSRUNFILES`, `DOSBUILDFILES`, `DESTDIR`, `INCLUDES`, `include ../tests.init`, targets `all`, `origtests`, `auxtests`, individual `test*` link rules, `lint`, `clean`, `copy`, and `dist`.

Control flow: `all` builds original and auxiliary tests then makes `runtests` executable. Each test links its matching `.c` file with `subr.o` and `$(LIBS)`. `lint` runs lint over each source; `copy` copies runnable files to `DESTDIR`; `dist` copies sources and extracts DOS support files into the destination.

State/persistence behavior: creates test binaries/object files, removes them on clean, and copies sources/binaries into distribution directories. Dependencies/integration: consumes compiler flags and libs from `../tests.init` and shared helper `subr.c`.

Risks/test signals: repetitive rules make omissions easy, `copy` depends only on `$(TESTS)` but copies `$(AUXTESTS)` too, and DOS file tar pipeline assumes matching files exist.
