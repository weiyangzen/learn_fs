# sources/test-tools/fs-mark/Makefile

Purpose: simple build/test Makefile for the `fs_mark` filesystem metadata benchmark.

Important targets/variables: `COBJS` lists `fs_mark.o lib_timing.o`. `CC`, `CFLAGS`, and `LDFLAGS` are overrideable; `CFLAGS` adds `-Wall -D_FILE_OFFSET_BITS=64`. `all` builds `fs_mark`. `fs_mark.o` depends on source/header. `fs_mark` links both objects. `test` runs four benchmark variants against `DIR1` and `DIR2` with fixed size/count and optional random names/subdirectories. `clean` removes objects, binary, and `fs_log.txt`.

Control flow/state: build is conventional compile/link. The `test` target writes many files under `/test/dir1` and `/test/dir2` by default and can fill or stress those filesystems.

Dependencies/integration: requires a C compiler, Linux-oriented headers used by fs_mark, writable test directories, and `lib_timing.c`.

Risks/test signals: default test directories are absolute and may not exist or may be unsafe on shared systems. Build smoke tests should override `DIR1`/`DIR2` to temporary paths.
