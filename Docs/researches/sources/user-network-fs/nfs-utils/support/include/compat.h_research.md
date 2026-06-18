# sources/user-network-fs/nfs-utils/support/include/compat.h

## Purpose
Provides small compatibility definitions missing from older system headers.

## Important APIs, Types, and Functions
Defines `NETLINK_EXT_ACK` as 11 when absent.

## Control Flow
Included before code calls `setsockopt(..., NETLINK_EXT_ACK, ...)` so older build hosts still compile.

## State and Persistence Behavior
No runtime state. It only affects preprocessing.

## Dependencies and Integration Points
Depends on `<linux/netlink.h>` and is used by netlink support such as cache flushing.

## Risks and Edge Cases
If a platform uses a different value, the fallback would be wrong; this mirrors Linux UAPI.

## Test Signals
Build against old and new kernel headers and verify netlink extended ACK setup compiles.
