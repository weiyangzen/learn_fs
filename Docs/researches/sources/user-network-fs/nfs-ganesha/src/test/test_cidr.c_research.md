# sources/user-network-fs/nfs-ganesha/src/test/test_cidr.c

Purpose: table-driven executable that exercises CIDR parsing, string formatting, and IPv4/IPv6 containment checks.

Important APIs, types, and functions: uses `cidr_from_str`, `cidr_to_str`, `cidr_contains_ip`, `cidr_free`, and `ip_str_to_sockaddr`. Test data includes invalid CIDR syntax, default masks, IPv4/IPv6 masks, IPv4-mapped IPv6, and zero masks.

Control flow: first loop parses CIDR strings and compares formatted output with expected values. Second loop parses a CIDR and an IP address, then checks containment return against expected boolean.

State and persistence: no persistent state; allocates/free CIDR objects and formatted strings per case.

Dependencies and integration points: depends on `ip_utils.h` and Ganesha memory wrappers.

Risks: failures only print messages and the program still exits with status 0, so CI will not fail unless output is inspected. The containment condition appears inverted: it prints "Failed" for `contains_ret && expected` and for `!contains_ret && !expected`, which may treat matching expected results as failures depending on `cidr_contains_ip` return convention. This test needs verification against the API contract.

Test signals: broad data coverage exists, especially for IPv6 mask edges, but executable exit semantics make the signal weak.
