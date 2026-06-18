# sources/user-network-fs/nfs-utils/support/include/nfsd_netlink.h

## Purpose
Generated Linux nfsd generic netlink UAPI mirror for server control, cache notifications, export/expkey requests, fs_locations, security flavors, and unlock commands.

## Important APIs, Types, and Functions
Defines family/version, cache types, export flags, xprtsec modes, many `NFSD_A_*` attribute enums, and `NFSD_CMD_*` commands.

## Control Flow
Netlink clients use these constants to subscribe to nfsd cache notifications, retrieve pending export/expkey requests, set responses, configure server threads/protocols/sockets, and flush caches.

## State and Persistence Behavior
No state. It encodes a kernel userspace ABI.

## Dependencies and Integration Points
Used by export cache netlink code, cache flushing, and nfsd control tools when system UAPI headers are unavailable.

## Risks and Edge Cases
Must remain synchronized with kernel `nfsd.yaml`. Attribute nesting and flag numeric alignment with `NFSEXP_*` are critical.

## Test Signals
Build with bundled/system UAPI switches and run netlink export cache, cache flush, and nfsdctl command tests.
