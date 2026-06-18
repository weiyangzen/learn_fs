# sources/user-network-fs/nfs-utils/support/include/lockd_netlink.h

## Purpose
Generated Linux UAPI mirror for lockd generic netlink commands.

## Important APIs, Types, and Functions
Defines `LOCKD_FAMILY_NAME`, version, server attributes, and server set/get commands.

## Control Flow
Consumers use these constants to build or parse generic netlink messages for lockd server configuration.

## State and Persistence Behavior
No runtime state; the header is an ABI constant set.

## Dependencies and Integration Points
Generated from kernel `lockd.yaml` and used by nfs-utils netlink tooling when system headers are unavailable.

## Risks and Edge Cases
Must track kernel UAPI. Manual edits risk command or attribute mismatch.

## Test Signals
Compile against bundled and system headers and test lockd netlink get/set message construction.
