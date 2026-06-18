# sources/user-network-fs/nfs-utils/support/reexport/Makefile.am

Purpose: `support/reexport/Makefile.am` builds the reexport support library and the `fsidd` helper daemon.

Important build APIs and control flow: It defines `libreexport.la` from `reexport.c`, `reexport.h`, and `reexport_backend.h`, and `fsidd` from `fsidd.c` plus `backend_sqlite.c`. `libreexport_la_CPPFLAGS` points at support headers, while `fsidd_LDADD` links SQLite, libevent, and support libraries.

State, dependencies, and integration: Build artifacts feed export parsing/mountd code through `libreexport.la`, while the installed daemon backs the AF_UNIX fsid service.

Risks and test signals: Runtime reexport support depends on both sqlite and libevent availability, and service/library version skew can break the text socket protocol. Tests should build with/without reexport dependencies, verify `fsidd` linkage, and run integration lookups against the library client.
