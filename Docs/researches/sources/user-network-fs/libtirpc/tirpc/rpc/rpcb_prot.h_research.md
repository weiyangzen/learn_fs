# sources/user-network-fs/libtirpc/tirpc/rpc/rpcb_prot.h

Purpose: `rpcb_prot.h` is rpcgen output for rpcbind protocol versions 3 and 4, including mapping records, remote-call wrappers, address-list records, statistics records, procedure stubs, and XDR prototypes.

Important APIs, types, and functions: It defines `struct rpcb`, list types `rpcblist`/`rpcblist_ptr`, `rpcb_rmtcallargs`, client-side `r_rpcb_rmtcallargs`, `rpcb_rmtcallres`, client-side `r_rpcb_rmtcallres`, `rpcb_entry`, stats list/types, `xdr_netbuf`, rpcbind socket paths, `RPCBPROG`, `RPCBVERS`, `RPCBVERS4`, procedure numbers, generated client/service stubs for v3/v4, and many `xdr_*` functions.

Control flow: Rpcbind v3 supports set/unset/getaddr/dump/callit/gettime/address conversion. Version 4 carries those plus broadcast alias, version-specific address lookup, non-quiet indirect calls, address-list lookup, and statistics retrieval. Generated stubs call these procedures through `CLIENT`, while `_svc` declarations define server dispatch hooks.

State and persistence behavior: The header defines wire and helper structures only. Runtime mapping tables and statistics persist in rpcbind. Linked-list results and string/netbuf fields are dynamically allocated during XDR decode and must be freed.

Dependencies and integration points: It includes `rpc/rpc.h` and therefore participates in a dense include graph. It is consumed by rpcbind client code, server code, generic service registration, and address conversion helpers.

Risks: It is generated and should be changed through the source `.x` file. The header contains separate kernel and non-kernel struct shapes, so conditional build paths must remain compatible. The abstract Unix socket string begins with `\0`, which requires length-aware handling. Linked list XDR is allocation-heavy and failure-prone if cleanup is missed.

Test signals: Tests should cover rpcgen regeneration, XDR round trips for maps/lists/entries/stats/netbuf, v3 and v4 stub linkage, abstract/local rpcbind socket connection, address list decode/free, and stats procedure compatibility.
