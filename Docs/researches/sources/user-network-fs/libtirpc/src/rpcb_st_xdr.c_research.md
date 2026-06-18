<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_st_xdr.c -->
# sources/user-network-fs/libtirpc/src/rpcb_st_xdr.c

Purpose: XDR support for rpcbind statistics structures generated from `rpcb_prot.x` and used by the rpcbind stats facility.

Important APIs and functions: `xdr_rpcbs_addrlist()`, `xdr_rpcbs_rmtcalllist()`, `xdr_rpcbs_proc()`, `xdr_rpcbs_addrlist_ptr()`, `xdr_rpcbs_rmtcalllist_ptr()`, `xdr_rpcb_stat()`, and `xdr_rpcb_stat_byvers()`.

Control flow: address and remote-call list nodes serialize program/version/procedure counters, success/failure/indirect counts, netid strings, and recursive next pointers. `xdr_rpcbs_rmtcalllist()` has optimized inline encode/decode paths for six fixed fields and a generic fallback. Stat arrays are handled through `xdr_vector`.

State and persistence: no static mutable state. XDR decode/free owns linked-list allocations through `xdr_pointer`.

Dependencies and integration points: depends on rpcbind stats typedefs and `RPCBSTAT_HIGHPROC`/`RPCBVERS_STAT` dimensions. It is consumed by rpcbind monitoring clients and servers rather than normal RPC call paths.

Risks: list serialization is recursive through `xdr_pointer`, so extremely long stats lists could recurse deeply. Inline decode assumes matching integer field order. Strings are bounded by `RPC_MAXDATASIZE` but can still allocate large buffers.

Test signals: encode/decode/free of empty and multi-node addr/rmtcall lists, vector dimensions for every rpcbind version, inline and non-inline XDR paths, and counter preservation for success/failure/indirect values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_st_xdr.c -->
