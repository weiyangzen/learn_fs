# sources/user-network-fs/nfs-utils/support/include/sunrpc_netlink.h

## Purpose
Generated Linux sunrpc cache generic netlink UAPI mirror for IP map, UNIX GID, cache notification, request subscription, and cache flush operations.

## Important APIs, Types, and Functions
Defines `SUNRPC_FAMILY_NAME`, cache types, `SUNRPC_A_*` attribute enums, `SUNRPC_CMD_*` commands, and multicast group names.

## Control Flow
Export/cache daemons use these constants to watch pending sunrpc cache requests, answer IP/GID mappings, receive notifications, or flush caches.

## State and Persistence Behavior
No runtime state. Constants describe kernel ABI.

## Dependencies and Integration Points
Used by export cache netlink processing and `cache_flush.c` fallback selection when system headers are unavailable.

## Risks and Edge Cases
Must track kernel `sunrpc_cache.yaml`; attribute mismatches break cache upcall handling.

## Test Signals
Build with bundled/system UAPI headers and test IP map, UNIX GID, notification, and flush netlink paths.
