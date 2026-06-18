# File Research: sources/os/bsd/netbsd-src/lib/libform/type_ipv4.c

Defines builtin `TYPE_IPV4`.

Field validation accepts three input styles:
- dotted quad: `a.b.c.d`
- classless/CIDR: `a.b.c.d/mask`
- hex: `0xaabbccdd`

It parses components, checks octets are <= 255 and masks <= 32, then normalizes buffer 0 to the input style’s canonical representation. If buffer 1 exists, it stores dotted-quad form there regardless of input style.

Character validation accepts hex digits, `.`, `x`/`X`, and `/`.
