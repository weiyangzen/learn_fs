# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_getport.c

Read completely: 132 lines.

Implements `pmap_getport()`, the legacy portmapper lookup for an IPv4 address, program, version, and protocol. It builds a `struct pmap`, sets the target address port to `PMAPPORT`, and calls `PMAPPROC_GETPORT`.

The initial client transport follows the requested protocol (`clnttcp_create()` for TCP, `clntudp_bufcreate()` otherwise). If the returned port is zero, it retries using the opposite transport. On RPC failure it sets `rpc_createerr.cf_stat = RPC_PMAPFAILURE`; on zero port it sets `RPC_PROGNOTREGISTERED`.

This provides old pmap behavior while using shared client constructors and global `rpc_createerr` state.
