# File Research: sources/os/bsd/netbsd-src/lib/librpcsvc/Makefile

Read completely: 41 lines.

Builds `librpcsvc` from a set of RPC `.x` interface definitions, generating headers and XDR source files through `bsd.rpc.mk`. Core RPC services include bootparam, KLM, mount, NFS, NLM, rex, rnusers/rusers, rquota, rstat, rwall, sm_inter, and spray.

When `MKYP` is enabled, YP and yppasswd RPC definitions and export symbols are added. The Makefile merges export-symbol fragments with `sort -m`, installs generated headers and `.x` files under `/usr/include/rpcsvc`, and builds the `rpcsvc` library with no manual page.
