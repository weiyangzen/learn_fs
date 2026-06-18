# sources/user-network-fs/rpcbind/src/rpcb_svc.c

## Purpose
Implements rpcbind version 3 service dispatch and version-3 local wrappers.

## APIs, Flow, And State
`rpcb_service_3` records procedure stats, chooses XDR argument/result routines and a common/local handler for each procedure, decodes arguments, extracts the program number for access checks on SET/UNSET/GETADDR, calls `check_access`, invokes the selected handler, sends replies, and frees arguments. It supports NULL, SET, UNSET, GETADDR, DUMP, CALLIT, GETTIME, UADDR2TADDR, and TADDR2UADDR. `rpcbproc_getaddr_3_local` logs caller address in debug and delegates to `rpcbproc_getaddr_com` with `RPCB_ALLVERS`. `rpcbproc_dump_3_local` returns `list_rbl`.

## Dependencies And Integration
Uses libtirpc XDR and SVC APIs, rpcbind common handlers (`rpcbproc_set_com`, `rpcbproc_unset_com`, conversion/time/getaddr helpers), stats, access checks, and global registration list state.

## Risks And Test Signals
The dispatcher relies on the union field matching selected XDR routines and on freeing decoded arguments exactly once. Authorization and version constants must align with stats and common handlers. Tests should cover each procedure, decode failures, weak-auth failures, dump output, and GETADDR version fallback behavior.
