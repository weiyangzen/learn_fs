# sources/user-network-fs/nfs-utils/support/include/sockaddr.h

## Purpose
Provides alias-safe socket address storage and inline helpers for address length, ports, equality, and loopback checks.

## Important APIs, Types, and Functions
`union nfs_sockaddr`, size macros, `nfs_sockaddr_length()`, `nfs_get_port()`, `nfs_set_port()`, `nfs_is_v4_loopback()`, `nfs_compare_sockaddr()`, and family-specific helpers.

## Control Flow
Callers store IPv4/IPv6 addresses in the union, query the family-specific length, get/set network-order ports, and compare addresses while respecting IPv6 link-local scope ids.

## State and Persistence Behavior
No state. It manipulates caller-owned sockaddr buffers.

## Dependencies and Integration Points
Used throughout client matching, hostname resolution, RPC helper code, and local-address checks.

## Risks and Edge Cases
The union is intentionally smaller than `sockaddr_storage` and unsuitable for AF_LOCAL. IPv6 helpers compile to no-ops/false when disabled.

## Test Signals
Test IPv4 and IPv6 length/port/equality, link-local scope mismatch, unsupported family handling, and no-IPv6 builds.
