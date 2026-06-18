# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpcb_st_xdr.c

Read completely: 279 lines.

Generated-from-RPCL XDR support for rpcbind statistics. It serializes address lookup stat lists, remote-call stat lists, per-procedure counters, per-version stats, and arrays of stats by rpcbind version.

Functions include `xdr_rpcbs_addrlist()`, `xdr_rpcbs_rmtcalllist()`, `xdr_rpcbs_proc()`, `xdr_rpcbs_addrlist_ptr()`, `xdr_rpcbs_rmtcalllist_ptr()`, `xdr_rpcb_stat()`, and `xdr_rpcb_stat_byvers()`. The remote-call list has inline encode/decode fast paths for its fixed numeric fields, then serializes `netid` and the next pointer.

This file is only for the rpcbind stats facility, not normal address lookup. Strings are bounded by `RPC_MAXDATASIZE`; linked lists use `xdr_pointer()` recursion.
