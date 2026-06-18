# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/if.c

Small network-interface iterator.

`if_map()`:
- Calls `getifaddrs()`.
- Iterates every `struct ifaddrs`.
- Invokes a caller callback with interface name, address pointer, and caller argument.
- Returns `-1` if `getifaddrs()` fails or if any callback returns `-1`; otherwise returns `0`.
- Frees the address list with `freeifaddrs()`.

No filtering is performed, so callbacks must handle null addresses and unsupported families.
