# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_prot.c

Read completely: 361 lines.

Implements XDR routines for rpcbind v3/v4 data structures: `xdr_rpcb()`, `xdr_rpcblist_ptr()`, `xdr_rpcblist()`, `xdr_rpcb_entry()`, `xdr_rpcb_entry_list_ptr()`, `xdr_rpcb_rmtcallargs()`, `xdr_rpcb_rmtcallres()`, and `xdr_netbuf()`.

Like the pmap list code, rpcbind map and entry-list serializers unwind pointer-recursive XDR lists into loops, with special handling for `XDR_FREE`. `xdr_rpcb_rmtcallargs()` writes the argument length after encoding by saving/restoring XDR stream positions. `xdr_netbuf()` bounds `maxlen` by `RPC_MAXDATASIZE` before serializing bytes.

This file is the main rpcbind wire-format implementation used by rpcbind clients, dumps, remote calls, and address conversion RPCs.
