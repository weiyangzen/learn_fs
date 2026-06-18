# sources/test-tools/xfstests-bld/fstests-bld/libinih/Makefile

Purpose: builds and installs a static `libinih.a` library from the vendored inih parser.

Important APIs, types, and functions: targets `libinih.a`, `install`, `clean`, and dependency `ini.o: ini.c ini.h`. Variables `OBJS`, `LIBDIR=$(DESTDIR)/lib`, and `INCDIR=$(DESTDIR)/include`.

Control flow: `libinih.a` archives `ini.o` with `ar rc` and indexes with `ranlib`; `install` creates lib/include dirs and copies `ini.h` and `libinih.a`; `clean` removes object and archive.

State and persistence: creates `ini.o`, `libinih.a`, and installed files under `DESTDIR`.

Dependencies and integration points: depends on the system `make`, compiler implicit rules, `ar`, and `ranlib`. Used by fstests-bld components needing INI parsing.

Risks: no explicit `CC`, `CFLAGS`, or install mode variables; relies on make defaults. `install` copies without rebuilding prerequisite unless invoked after archive target. No `mkdir -p` for object dir needed because it builds in place.

Test signals: run `make`, `make install DESTDIR=/tmp/...`, compile a small program against installed header and archive, and run `make clean`.
