# sources/user-network-fs/nfs-utils/support/include/rpcmisc.h

## Purpose
Declares shared RPC server registration and dispatch helpers.

## Important APIs, Types, and Functions
Defines `rpcsvc_fn_t`, `struct rpc_dentry`, `struct rpc_dtable`, `dtable_ent()` macro, service create/unregister/init/dispatch functions, globals for rpcbind/service state, and caller sockaddr helpers.

## Control Flow
Daemons build dispatch tables from XDR and service functions, register RPC programs/transports, and dispatch incoming requests through `rpc_dispatch()` by procedure number.

## State and Persistence Behavior
Global `_rpcpmstart`, `_rpcprotobits`, and `_rpcsvcdirty` track RPC service setup. Server registration persists in rpcbind/portmap until unregistered.

## Dependencies and Integration Points
Depends on libtirpc/SunRPC server headers. Used by statd, mountd, and other RPC daemons.

## Risks and Edge Cases
Procedure table sizes and XDR function casts must match generated RPC code. Caller sockaddr helpers expose transport-owned storage.

## Test Signals
Test service registration/unregistration, dispatch of known and unknown procedures, XDR decode failures, and caller address extraction.
