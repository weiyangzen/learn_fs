# sources/user-network-fs/nfs-utils/support/export/client.c

## Purpose
Maintains the in-memory client table used by export matching. It classifies export host identifiers as FQDNs, subnetworks, wildcards, netgroups, anonymous clients, or GSS principals, then resolves and matches callers against those records.

## Important APIs, Types, and Functions
Public functions are `client_lookup()`, `client_dup()`, `client_gettype()`, `client_check()`, `client_release()`, `client_freeall()`, `client_resolve()`, `client_compose()`, and `client_member()`. Core helpers initialize address lists, parse IPv4/IPv6 netmasks, test wildcard/netgroup membership, and maintain sorted comma-separated names.

## Control Flow
`client_lookup()` classifies the host string, resolves FQDNs when needed, searches `clientlist[type]`, allocates a new `nfs_client` when absent, and populates addresses. `client_check()` dispatches by type: exact address comparison for FQDNs, mask matching for subnetworks, reverse DNS plus aliases for wildcards, `innetgr()` variants for netgroups, and unconditional match for anonymous clients.

## State and Persistence Behavior
`clientlist[MCL_MAXTYPES]` is a process-global linked-list table. Each `nfs_client` owns a hostname string, address union array, exported flag, and reference count incremented by exports. State is freed by `client_freeall()` after export teardown.

## Dependencies and Integration Points
Depends on `sockaddr.h` address helpers, host resolution functions from `hostname.c`, `wildmat()`, libc resolver APIs, optional IPv6 and netgroup support, and `exportfs.h` structures. It is consumed by `export.c`, auth/cache matching, and etab rebuilds.

## Risks and Edge Cases
DNS and netgroup lookups can block or fail. Netmask parsing has family-specific rules and IPv6 code depends on compile flags. `client_member()` only matches comma-delimited exact names. The fallback netgroup IP check treats the first sockaddr as IPv4-shaped for `inet_ntop`, so mixed-family handling deserves care.

## Test Signals
Test identifier classification, IPv4 prefix and dotted masks, IPv6 prefix and explicit masks, wildcard aliases, netgroup present/absent builds, anonymous and GSS behavior, duplicate lookup reuse, and sorted `client_compose()` output.
