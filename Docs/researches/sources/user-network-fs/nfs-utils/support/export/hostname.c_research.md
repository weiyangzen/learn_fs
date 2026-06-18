# sources/user-network-fs/nfs-utils/support/export/hostname.c

## Purpose
Centralizes hostname and numeric address conversion for export client matching, including strict presentation parsing and reliable reverse/forward lookup checks.

## Important APIs, Types, and Functions
Public functions are `host_ntop()`, `host_pton()`, `host_addrinfo()`, `host_canonname()`, `host_reliable_addrinfo()`, and `host_numeric_addrinfo()`.

## Control Flow
`host_pton()` first uses strict `inet_pton()` for IPv4 validation before `getaddrinfo(AI_NUMERICHOST)` to avoid accepting partial IPv4 strings. `host_addrinfo()` resolves names with canonical names. `host_reliable_addrinfo()` reverse-resolves an address, resolves that hostname forward, verifies the original address is present, then returns numeric addrinfo for the original sockaddr.

## State and Persistence Behavior
All returned names and addrinfo lists are heap-owned by callers. There is no global cache. Logging records resolver failures at parse/general debug levels.

## Dependencies and Integration Points
Depends on `sockaddr.h`, libc resolver APIs, optional `getnameinfo()`, `inet_ntop()`, `inet_pton()`, and `nfs_compare_sockaddr()`. Used heavily by `client.c` and auth matching.

## Risks and Edge Cases
DNS behavior can be slow or environment-dependent. Fallback code supports only IPv4. `host_pton()` deliberately rejects some strings `getaddrinfo()` would accept, which can surprise callers expecting legacy abbreviated IPv4.

## Test Signals
Test numeric IPv4/IPv6 conversion, invalid partial IPv4 such as `10.4`, reverse lookup failure, forward/reverse mismatch, unsupported families, and builds with and without `getnameinfo()`.
