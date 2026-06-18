<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mount_dispatch.c -->
# sources/user-network-fs/nfs-utils/utils/mountd/mount_dispatch.c

## Purpose

`mount_dispatch.c` defines the RPC dispatch tables for the MOUNT protocol versions served by `rpc.mountd` and forwards accepted requests to the generic RPC dispatcher.

## Important APIs, types, and functions

It declares static `rpc_dentry` arrays for MNTv1, MNTv2, and MNTv3. The arrays map procedure numbers to service functions such as `mount_null`, `mount_mnt`, `mount_dump`, `mount_umnt`, `mount_export`, and v2 `mount_pathconf`. Public function `mount_dispatch` performs optional tcp-wrapper authorization and calls `rpc_dispatch`.

## Control flow

Incoming RPC requests enter `mount_dispatch`. If tcp-wrapper support is compiled in, the caller address is checked for service `mountd`; failed clients receive `AUTH_FAILED`. Accepted requests are dispatched by version/procedure lookup using the table array.

## State and persistence behavior

The file has only static dispatch metadata. It does not mutate persistent state; invoked service handlers in `mountd.c` and `rmtab.c` may update rmtab or export caches.

## Dependencies and integration points

It depends on `mountd.h`, `rpcmisc.h`, tirpc/SunRPC types, and optional `tcpwrapper.h`. It is registered as the dispatch callback when `mountd.c` creates listeners for MOUNTPROG versions.

## Risks and edge cases

Incorrect table sizes or procedure/type mappings would decode RPC arguments incorrectly. Tcp-wrapper failures occur before service-level authentication, so wrapper configuration can block otherwise valid exports. MNTv3 omits EXPORTALL and PATHCONF compared to earlier versions.

## Test signals

Tests should send NULL, MNT, DUMP, UMNT, UMNTALL, EXPORT, EXPORTALL, and PATHCONF calls for supported versions, plus invalid procedure/version calls and tcp-wrapper denial where compiled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mount_dispatch.c -->
