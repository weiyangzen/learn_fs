# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_cidr_pton.c

Implements `inet_cidr_pton`, parsing IPv4/IPv6 CIDR presentation strings into binary address plus prefix length.

Behavior:
- Dispatches by address family.
- IPv4 parser accepts dotted decimal octets and optional `/bits`; defaults to `/32` only when all four octets are specified.
- IPv6 parser handles `::`, hex words, embedded IPv4, and optional `/bits`.
- `getbits` rejects empty values, leading zeros, and out-of-range widths.
- Returns `0` on success and `-1` with `ENOENT`, `EMSGSIZE`, or `EAFNOSUPPORT` on failure.

Notable: IPv6 parser stores `bits = -1` if no prefix was supplied; callers receive that value.
