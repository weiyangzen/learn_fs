# sources/user-network-fs/nfs-utils/support/include/tcpwrapper.h

## Purpose
Declares TCP wrapper/local-address access checks used by RPC daemons.

## Important APIs, Types, and Functions
`from_local()` tests whether a sockaddr belongs to the local host. `check_default()` checks access policy for a service/program and caller address.

## Control Flow
Callers typically allow local callers or consult hosts.allow/hosts.deny style policy through the implementation.

## State and Persistence Behavior
Implementation may cache local interface addresses and access decisions. Policy files are external persistent state.

## Dependencies and Integration Points
Used by mountd/statd RPC access paths. Depends on socket headers and `from_local.c`/`tcpwrapper.c` implementations.

## Risks and Edge Cases
Policy evaluation depends on system tcp_wrappers availability and current interface list. Address-family handling must match callers.

## Test Signals
Test local/remote address detection, policy allow/deny files, IPv4/IPv6 callers, and interface address cache refresh.
