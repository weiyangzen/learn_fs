# sources/security-integrity/audit-userspace/src/libev/Makefile.am

Purpose: defines the Automake build recipe for the bundled libev convenience library used by audit-userspace. It builds a static, non-installed libtool archive from the libev core and libevent compatibility layer.

Important build variables: `VERSION_INFO = 4:0:0`, `EXTRA_DIST` ships backend source files and `libev.m4`, `AM_CFLAGS` enables PIC, debug info, no strict aliasing, and suppresses unused-value warnings, `noinst_HEADERS` lists `ev.h`, `ev_vars.h`, `ev_wrap.h`, and `event.h`, and `noinst_LTLIBRARIES = libev.la` declares the internal library.

Control flow: Automake consumes this file during configure/make generation. `libev_la_SOURCES = ev.c event.c` compiles the core translation unit and compatibility layer; the backend files are not separate compilation units because `ev.c` includes selected backends directly under compile-time feature macros. `libev_la_LDFLAGS = -no-undefined -static` requests a static libtool archive with resolved symbols.

State and persistence: this file does not manage runtime state. It controls generated build artifacts and distribution contents, including ensuring backend files are included in tarballs even when not separately compiled.

Dependencies and integration: integrates the vendored libev subtree into the audit-userspace Automake/libtool build. The `-fno-strict-aliasing` flag matches libev's watcher-casting style, and `-DPIC -fPIC` supports linking into other audit-userspace objects.

Risks: backend files must remain in `EXTRA_DIST` because they are included by `ev.c`; omitting one can break distribution builds without affecting in-tree builds. `event.h` is listed but not in this work item; compatibility consumers depend on it matching `event.c`. Static linkage and local CFLAGS can diverge from system libev behavior.

Test signals: run `autoreconf`/`configure` and `make` from a clean distribution tree, verify `libev.la` builds from `ev.c` and `event.c`, and run `make distcheck` to catch missing `EXTRA_DIST` files.
