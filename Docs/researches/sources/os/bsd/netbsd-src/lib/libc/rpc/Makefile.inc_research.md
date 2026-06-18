# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/Makefile.inc

Read completely: 180 lines.

This make include adds libc RPC sources, defines `PORTMAP`, installs RPC-related man pages, and creates extensive manual-page links for client, server, rpcbind, and XDR APIs.

Key behavior: `SRCS` covers authentication, client transports, rpcbind/portmap, service transports, common RPC data, XDR implementations, and `__rpc_getxid.c`. `MLINKS` maps historical API names to grouped manuals. Per-file compiler warning suppressions are set for several cast-heavy legacy RPC files.

Important interactions: build composition for all RPC files in this group; `PORTMAP` enables legacy portmap behavior in files such as `clnt_bcast.c`.

Security/reliability notes: no runtime logic, but build flags affect legacy protocol compatibility and exported libc API coverage.
