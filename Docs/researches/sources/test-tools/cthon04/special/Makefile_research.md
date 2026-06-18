# sources/test-tools/cthon04/special/Makefile

## Purpose
This Makefile builds and distributes the Connectathon special-case filesystem test programs. It covers open-unlink/rename/chmod behavior, duplicate requests, exclusive create, negative seek, sparse files, truncate, idempotency, stat timing, directory cookies, large files, and free-space truncation.

## Important APIs, Types, and Functions
Key variables are `TESTS`, `DOSRUNFILES`, `DOSBUILDFILES`, `DESTDIR`, `COPYFILES`, `INCLUDES`, `SUBRS`, and `DEPS`. Targets include one executable rule for each C source, `../basic/subr.o`, `all`, `lint`, `clean`, `copy`, and `dist`.

## Control Flow and State
`all` builds every program and ensures `runtests` is executable. Most rules compile `$@.c` with inherited `$(CC) $(CFLAGS) $(LIBS)` from `../tests.init`; programs that use timing/tree helpers link `../basic/subr.o`. Distribution targets copy either binaries plus run files or full sources plus DOS/console build files into `DESTDIR`.

## Persistence and Dependencies
It persists compiler outputs, executable test binaries, and copied distribution trees; `clean` removes objects, test binaries, and several scratch names. Dependencies: `../tests.init`, `../tests.h`, `../basic/subr.o`, standard make, C compiler/libraries, and DOS/Win build artifact directories.

## Integration Points, Risks, and Test Signals
Integration is with `special/runtests` and top-level Connectathon builds. Risks include assuming source and binary names match, `DESTDIR=/no/such/path` unless overridden, copy/dist commands that remove files at the destination, no dependency tracking beyond the shared header/subr object, and platform-specific tests that compile but skip at runtime. Test signals are successful `make all`, executable `runtests`, clean `make copy DESTDIR=...`, and expected no-op skips for unsupported platform features.
