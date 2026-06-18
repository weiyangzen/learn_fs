# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/wol.c

## Purpose
Sends Wake-on-LAN magic packets.

## Behavior
Builds a packet containing six `0xff` bytes, sixteen copies of the parsed Ethernet address, and an optional six-byte password. Defaults to dialing `udp!255.255.255.255!0`, or uses `-a dialstr`. `-c` supplies the password and `-v` prints packet details.

## Dependencies
Uses `parseether`, `dial`, Plan 9 IP formatting, and writes the packed structure directly to the UDP connection.
