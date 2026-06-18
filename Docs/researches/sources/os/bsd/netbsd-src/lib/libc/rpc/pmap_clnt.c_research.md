# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_clnt.c

Read completely: 127 lines.

Implements legacy portmapper registration wrappers `pmap_set()` and `pmap_unset()` on top of rpcbind. `pmap_set()` accepts only UDP or TCP, obtains the matching IPv4 netconfig via `__rpc_getconfip()`, converts a port into a universal address of the form `0.0.0.0.hi.lo`, converts that to a transport address with `uaddr2taddr()`, and calls `rpcb_set()`.

`pmap_unset()` attempts to remove the mapping for both UDP and TCP rpcbind netconfigs and returns success if either unset succeeds, preserving backward-compatible semantics.

The file is compatibility glue; modern address registration is delegated to rpcbind APIs and netconfig conversion helpers.
