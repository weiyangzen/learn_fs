# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/testlook.c

`testlook.c` is an older/test utility for NDB IP information lookup.

Key behavior:
- Contains helper functions to find values in NDB tuples, resolve names to IPs, and recursively inspect subnet records.
- A large `ipinfo` implementation is wrapped in `#ifdef foo`, so it is disabled in this file.
- `main` opens NDB, selects lookup by IP-looking argument or Ethernet-looking argument, calls `ipinfo`, and prints address/mask/net/bootfile/Ethernet.

Important dependencies:
- Uses Plan 9 NDB and IP formatting APIs.

Notable risks/quirks:
- As written, it calls `ipinfo` even though its local implementation is disabled; it depends on an external/library `ipinfo` symbol.
- Includes debug `print("%s->", ip)` in subnet recursion.
