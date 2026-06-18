# File Research: sources/os/bsd/netbsd-src/lib/libform/type_ipv6.c

Defines builtin `TYPE_IPV6`.

Field validation uses `getaddrinfo` with `AF_INET6` and `AI_NUMERICHOST` to require a numeric IPv6 literal, rejects results with multiple addresses, then formats the address with `getnameinfo(..., NI_NUMERICHOST)` and writes the normalized text to buffer 0.

Character validation accepts hex digits, `.`, and `:`.
