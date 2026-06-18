# File Research: sources/os/plan9/9front/sys/src/cmd/ip/wol.c

This sends Wake-on-LAN magic packets.

Key behavior:
- Parses a target Ethernet MAC address.
- Builds the standard packet: six `0xff` bytes followed by the MAC repeated 16 times.
- Optional `-c` appends a password up to six bytes.
- Optional `-a` overrides the default destination `udp!255.255.255.255!0`.
- Optional `-v` prints packet details.

Research notes:
- Uses Plan 9 `%E` formatting for Ethernet addresses.
