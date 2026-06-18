# sources/user-network-fs/nfs-utils/support/include/nfsrpc.h

## Purpose
Declares RPC client utility functions for NFS, mount, lockd, statd, rpcbind, and portmap interactions.

## Important APIs, Types, and Functions
Defines program constants, `NFSPROTO_RDMA`, `nfs_clear_rpc_createerr()`, RPC client constructors, netid/protocol conversion, universal address helpers, port lookup/ping APIs, statd probe, and `nfs_authsys_create()`.

## Control Flow
Callers resolve program names, acquire privileged or ephemeral RPC clients, map service tuples to ports through rpcbind/portmap, ping remote services, and create AUTH_SYS handles.

## State and Persistence Behavior
No state except libc/libtirpc `rpc_createerr`, cleared by inline helper. Network queries observe remote rpcbind/statd state.

## Dependencies and Integration Points
Depends on libtirpc/SunRPC headers and socket address data. Used by mount, statd, lockd, and NFS service discovery code.

## Risks and Edge Cases
RPC timeouts, privileged port binding, IPv6/universal address formatting, and RDMA pseudo-protocol handling are portability risks.

## Test Signals
Test tcp/udp/rdma netid conversion, rpcbind and portmap lookups, ping timeouts, privileged client binding, and statd probe behavior.
