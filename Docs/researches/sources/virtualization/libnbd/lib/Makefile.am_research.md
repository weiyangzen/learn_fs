# File Research: sources/virtualization/libnbd/lib/Makefile.am

Build recipe for the core libnbd library. It declares generated sources (`api.c`, `states.c`, `states-run.c`, `states.h`, `unlocked.h`), hand-written library sources, pkg-config output, and two fork-safety unit tests.

Key points:
- Builds `libnbd.la` from connection, TLS, debug, error, flag, handle, option, polling, protocol, read/write, socket, URI, utility, and generated state-machine files.
- Adds includes from public headers and common utility directories.
- Links against common utils, pthreads, GnuTLS, and libxml2 when configured.
- Installs `libnbd.pc`.
- Test programs compile `errors.c` and `utils.c` directly with small focused test drivers.

Dependencies:
- Autotools/libtool variables, generated state-machine files, `common/utils/libutils.la`, GnuTLS/libxml2 configure substitutions.

Research notes:
- This file is the manifest showing the library architecture: generated API/state code plus small hand-written modules around handle state, transport, protocol, and utilities.
