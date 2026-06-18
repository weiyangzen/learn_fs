# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_net_pton.c

Implements `inet_net_pton`, parsing IPv4/IPv6 network numbers and returning prefix length.

IPv4 behavior:
- Accepts hex strings (`0x...`), decimal dotted forms, and optional `/CIDR`.
- Infers classful prefix length when CIDR is absent.
- Extends the destination with zero bytes up to the inferred/specified mask.
- Returns prefix length, or `-1` with `ENOENT`/`EMSGSIZE`.

IPv6 behavior:
- Handles `::`, hex words, optional embedded IPv4, and `/bits`.
- Defaults missing bits to `/128`.
- Copies only the number of bytes needed for the prefix.
- Requires the parsed address shape to match the prefix-derived word count.

Unsupported families set `EAFNOSUPPORT`.
