# File Research: sources/virtualization/nbd/tests/code/clientacl.c

## Purpose
Tests `address_matches()` CIDR matching behavior for IPv4, IPv4-mapped IPv6, and negative cases.

## Main Entry Points
- `do_test()` resolves an address, prints numeric resolved forms, and checks each result against a netmask.
- `main()` runs expected-match and expected-nonmatch cases.

## Dependencies
Uses `getaddrinfo()`, `getnameinfo()`, and `address_matches()` from the server helper library.

## Risks and Notes
The test exits immediately on name-resolution errors. It intentionally validates IPv4-mapped IPv6 compatibility.
