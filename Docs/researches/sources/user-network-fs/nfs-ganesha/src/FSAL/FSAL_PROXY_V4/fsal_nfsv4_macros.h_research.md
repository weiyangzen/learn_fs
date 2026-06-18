# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/fsal_nfsv4_macros.h

## Purpose
Defines macro helpers for constructing NFSv4/NFSv4.1 COMPOUND argument arrays in FSAL_PROXY_V4. The macros cover session sequencing, client/session setup, filehandle selection, lookup, open/create, read/write, directory, link, remove, rename, setattr, readlink, and commit operations.

## Important APIs, Types, and Functions
Key macros include `COMPOUNDV4_ARG_ADD_OP_SEQUENCE`, `COMPOUNDV4_ARG_ADD_OP_CREATE_SESSION`, `COMPOUNDV4_ARG_ADD_OP_PUTFH`, `COMPOUNDV4_ARG_ADD_OP_GETFH`, `COMPOUNDV4_ARG_ADD_OP_GETATTR`, `COMPOUNDV4_ARGS_ADD_OP_OPEN_4_1`, `COMPOUNDV4_ARG_ADD_OP_READ`, `COMPOUNDV4_ARG_ADD_OP_WRITE`, and `COMPOUNDV4_ARG_ADD_OP_SETATTR`. They write `nfs_argop4` union arms and increment caller-owned operation counters.

## Control Flow
Callers allocate an op array, pass an op counter, and invoke macros in NFSv4 compound order. `SEQUENCE` slot and sequence ids are intentionally filled later by `proxyv4_compoundv4_execute` after it chooses a free RPC IO context.

## State and Persistence Behavior
No persistent state exists. The macros mutate caller stack/heap argument arrays and often store pointers to caller-owned name/iovec/attribute buffers until XDR encoding.

## Dependencies and Integration Points
Depends on `gsh_rpc.h`, `nfs4.h`, and `fsal.h`. It is heavily consumed by `handle.c` for every remote NFS operation.

## Risks
Macro use provides little type/lifetime checking, does not always clear unused union fields, and requires referenced strings and buffers to remain alive. The write macro appears to set a stateid sequence field through the `opread` union member while building `OP_WRITE`, which is suspicious and worth review.

## Test Signals
No direct tests. Integration signals are successful proxy lookup/open/create/readdir/read/write/setattr/commit flows and no XDR encode/decode failures.
