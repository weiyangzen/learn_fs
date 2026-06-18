# sources/user-network-fs/rpcbind/src/rpcb_svc_4.c

## Purpose
Implements rpcbind version 4 service dispatch and version-4-only address lookup procedures.

## APIs, Flow, And State
`rpcb_service_4` dispatches NULL, SET, UNSET, GETADDR, GETVERSADDR, DUMP, INDIRECT, BCAST, GETTIME, UADDR2TADDR, TADDR2UADDR, GETADDRLIST, and GETSTAT. Like version 3 it selects XDR handlers, decodes, authorizes, invokes local/common handlers, sends replies, and frees args. `rpcbproc_getaddr_4_local` allows any version via `RPCB_ALLVERS`; `rpcbproc_getversaddr_4_local` requires one version via `RPCB_ONEVERS`. `rpcbproc_getaddrlist_4_local` builds a static response list of merged addresses for all registered mappings with the same program/version and protocol family as the request transport, deleting dead registrations and updating stats. `free_rpcb_entry_list` frees allocated merged-address entries, and dump returns `list_rbl`.

## Dependencies And Integration
Uses rpcbind common service functions, `mergeaddr`, `rpcbind_get_conf`, registration list globals, GETSTAT from `rpcb_stat.c`, and libtirpc XDR/SVC types.

## Risks And Test Signals
`GETADDRLIST` uses static response storage and must free prior allocations before rebuilding. It stores pointers to netconfig fields and allocated merged addresses, making ownership discipline important. Tests should cover address-list filtering by protocol family, dead-service deletion, stat updates, GETVERSADDR strictness, and all dispatch authorization/error paths.
