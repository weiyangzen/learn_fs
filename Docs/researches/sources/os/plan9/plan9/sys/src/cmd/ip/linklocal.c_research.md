# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/linklocal.c

Small command that prints IPv6 link-local or 6to4 addresses derived from Ethernet MAC addresses.

Key behavior:
- `ea2eui64` expands MAC-48 to EUI-64 and flips the universal/local bit for IPv6.
- `ea2lla` builds `fe80::/64` link-local addresses from MACs.
- `eaip26to4` builds `2002:<ipv4>::/48` 6to4-style addresses and appends EUI-64 interface ID.
- `main` accepts `-t ipv4` for 6to4 mode and one or more Ethernet addresses.

Integration points:
- Uses Plan 9 IP formatting/parsing helpers `parseether`, `v4parseip`, `%I`.

Risks and notes:
- No explicit validation of `-t` parse success beyond `v4parseip` call behavior.
