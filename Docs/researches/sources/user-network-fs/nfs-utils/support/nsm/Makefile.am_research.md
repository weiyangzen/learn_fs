# sources/user-network-fs/nfs-utils/support/nsm/Makefile.am

Purpose: `support/nsm/Makefile.am` builds the internal NSM support library used by statd and tests.

Important build APIs and control flow: It defines generated RPC files from `sm_inter.x`, builds `libnsm.a` from generated files plus `file.c` and `rpc.c`, and handles either an in-tree rpcgen or an external `@RPCGEN_PATH@`. Rules generate client, service, XDR, and header outputs, and a `sm_inter.h` rule appends an `sm_prog_1` prototype and links it into `support/include`.

State, dependencies, and integration: Generated sources are build-state artifacts and are removed via `CLEANFILES`. The library links conceptually into rpc.statd, sm-notify, and NSM tests.

Risks and test signals: Generated-file ordering depends on `BUILT_SOURCES` and rpcgen availability. The header rule mutates generated output after rpcgen. Tests should run `make distcheck`, clean rebuilds with in-tree and system rpcgen, and verify `support/include/sm_inter.h` exists.
