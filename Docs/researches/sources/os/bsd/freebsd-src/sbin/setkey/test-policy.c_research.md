# File Research: sources/os/bsd/freebsd-src/sbin/setkey/test-policy.c

## Summary
Standalone test program for libipsec policy parsing and socket IPsec policy set/get behavior.

## Main Elements
- Defines a list of valid and intentionally invalid policy request strings.
- Converts each request through `ipsec_get_policylen()` and `ipsec_set_policy()`.
- Applies generated policies to IPv4 and IPv6 datagram sockets with `setsockopt()`.
- Reads policies back with `getsockopt()`.
- Dumps returned policies using `ipsec_dump_policy()`.

## Dependencies And Integration
Uses `libipsec`, PF_KEY policy length macros, IPv4/IPv6 IPsec socket options, and direct sockets.

## Research Notes
The tests include malformed policy strings and a very long policy request to exercise parser error handling and policy buffer behavior.
