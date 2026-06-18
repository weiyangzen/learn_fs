# sources/storage-engines/lmdb/libraries/liblmdb/Makefile

## Purpose
Builds and installs the LMDB C library, command-line tools, test programs, optional remap/encryption tests, coverage artifacts, and a `pkg-config` file.

## Important APIs, Types, And Functions
Important variables include `CC`, `AR`, warning flags, `THREADS`, `CFLAGS`, `LDFLAGS`, `LIBVER`, `ABIVER`, `LMDB_VERSION`, installation directories, and library/tool lists. Targets build `liblmdb.a`, `liblmdb.so.1.0`, `mdb_stat`, `mdb_copy`, `mdb_dump`, `mdb_load`, `mdb_drop`, `mtest*`, `mtest_remap`, encryption tests, `crypto.lm`, `lmdb.pc`, and coverage binaries.

## Control Flow
`all` builds libraries, tools, and `lmdb.pc`. `install` creates destination directories, copies binaries/headers/manpages, and creates shared-library symlinks. Pattern rules compile `.c` to `.o`; PIC-specific rules build `.lo`; shared library rules link with soname flags. `test` creates `testdb`, runs `mtest`, then `mdb_stat`.

## State And Persistence Behavior
Build artifacts are written in-place. `test` creates/removes `testdb`. `install` writes under `DESTDIR` plus configured prefixes. `clean` removes binaries, objects, shared libraries, temporary files, and `testdb`.

## Dependencies And Integration Points
The makefile integrates `mdb.c`, `midl.c`, `module.c`, public `lmdb.h`, utilities, manpages, `libsodium` for `crypto.lm`, and `dlopen` support through `-ldl`. It supports optional `MDB_VL32` and `MDB_RPAGE_CACHE` modes via `CPPFLAGS`.

## Risks And Edge Cases
The static library references `module.o`, but the source list in this directory must contain it for builds to succeed. Encryption test link rules depend on `crypto.lm` but do not link it directly into every command line, implying runtime module loading. `clean` is broad and removes matching local artifacts.

## Test Signals
`make test` is the minimal smoke signal. Successful `all`, `rall`, encryption test builds, generated `lmdb.pc`, and coverage targets provide broader build integration signals.
