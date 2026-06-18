# sources/user-network-fs/nfs-utils/support/misc/from_local.c

## Purpose
Determines whether a sockaddr belongs to a local network interface for tcpwrapper/access-control decisions.

## Important APIs, Types, and Functions
`from_local()` is the public API. With `getifaddrs()` it caches the interface list for one-second granularity; fallback code uses ioctl `SIOCGIFCONF` and stores IPv4 addresses in a growable static array.

## Control Flow
On each call, the getifaddrs path refreshes cached addresses when `time()` changes, then compares active interface addresses with `nfs_compare_sockaddr()`. The fallback discovers active IPv4 interfaces once and compares raw IPv4 addresses.

## State and Persistence Behavior
Static cache state includes interface list/time or fallback address arrays. No persistent files are modified.

## Dependencies and Integration Points
Depends on `sockaddr.h`, interface APIs, ioctl fallback, and `xlog`. Declared by `tcpwrapper.h` and used by RPC access checks.

## Risks and Edge Cases
Cache refresh frequency can miss rapid interface changes. Fallback supports only IPv4. `ifa_addr` NULL handling is not explicit before comparison. Time failure reuses cache when possible.

## Test Signals
Test local loopback/interface addresses, remote addresses, interface down/up changes, IPv6 with getifaddrs, fallback IPv4 builds, and getifaddrs/ioctl failure handling.
