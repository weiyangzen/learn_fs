<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.h -->
# sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.h

## Purpose

`nfssvc.h` declares the internal service-control interface used by `rpc.nfsd`.

## Important APIs, types, and functions

It declares functions for mounting nfsdfs, checking active sockets, setting sockets and RDMA port, setting grace/lease times, configuring NFS major/minor versions, changing kernel thread count, reading minor-version masks, and setting a filehandle key.

## Control flow

No executable flow exists. `nfsd.c` calls these functions in a strict order: mount nfsdfs, check in-use status, set versions/timeouts, set sockets/RDMA, then set threads.

## State and persistence behavior

The declared functions mutate kernel nfsd procfs state. The header itself holds no state.

## Dependencies and integration points

It is the boundary between argument/config parsing in `nfsd.c` and procfs writes in `nfssvc.c`.

## Risks and edge cases

The header declares `nfssvc_setfh_key`, but this work-item source set does not include an implementation in `nfssvc.c`, so link coverage elsewhere is required. Callers must understand which functions return errno-style values and which only log.

## Test signals

Compile/link tests should ensure all declared functions are defined in the complete build. Unit tests should verify caller handling of return values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.h -->
