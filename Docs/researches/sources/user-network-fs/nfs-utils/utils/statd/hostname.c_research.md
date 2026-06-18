## sources/user-network-fs/nfs-utils/utils/statd/hostname.c

Purpose: Provides hostname/address canonicalization and equivalence checks for statd monitor matching.

Important APIs/types/functions: `statd_present_address`, `statd_canonical_name`, `statd_matchhostname`, and internal `get_addrinfo`, `get_nameinfo`, `statd_canonical_list`.

Control flow: Presentation addresses are converted with getnameinfo when available; canonical name resolution distinguishes numeric hosts from names; matching first checks case-insensitive string equality, then canonical names, then address-list intersection.

State and persistence: No state; DNS and resolver configuration are external state.

Dependencies and integration: Uses nfs-utils sockaddr helpers, `getaddrinfo`/`getnameinfo`, IPv6 build flags, and `xlog`. Called by monitor registration, unmonitor, notify handling, and list search.

Risks and test signals: DNS latency blocks the single-threaded daemon, reverse/forward mismatch affects correctness, wildcard/netgroup comments are not explicitly enforced here, and IPv6 fallback behavior differs by build. Tests should cover numeric IPv4/IPv6, no reverse DNS, canonical aliases, same-address different names, resolver failures, and scope IDs.
