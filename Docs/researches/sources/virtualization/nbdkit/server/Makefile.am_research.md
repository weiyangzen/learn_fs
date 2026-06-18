# File Research: sources/virtualization/nbdkit/server/Makefile.am

Builds the main `nbdkit` server executable and its small unit test.

Key behavior:
- Distributes `nbdkit.syms`.
- Builds `sbin_PROGRAMS = nbdkit` from core server sources including backend/filter/plugin management, protocol handshakes, sockets, TLS/crypto, logging, options, parsing, password, thread-local connection state, signals, URI, user/group, and public API support.
- Adds `fuzzer.c` when `ENABLE_LIBFUZZER` is enabled.
- Defines install path macros (`bindir`, `libdir`, `plugindir`, etc.).
- Includes public headers, common protocol, replacements, and utils.
- Links pthreads, GnuTLS, SELinux, valgrind flags where configured, dl/rt/bsd libs, common protocol/utils/replacements libraries, and math library.
- Applies the server linker version script when enabled.
- On Windows, generates `libnbdkit.a` import library and `nbdkit.def` from `nbdkit.syms`.
- Generates `synopsis.c` from `docs/synopsis.txt`.
- Defines `pkgconfig_DATA = nbdkit.pc`.
- Builds and runs `test-public` from selected public API/support sources.

Dependencies:
- Common nbdkit libraries.
- Optional GnuTLS, SELinux, valgrind, libfuzzer, Windows dlltool.
- POD/manpage generation handled elsewhere, not in this file.
