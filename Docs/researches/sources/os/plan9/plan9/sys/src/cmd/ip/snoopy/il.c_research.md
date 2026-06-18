# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/il.c

`snoopy` decoder for Plan 9 IL transport packets.

Key behavior:
- Parses checksum, length, type, special byte, source/destination ports, id, and ack.
- Filters on source, destination, or either port.
- Demuxes selected Plan 9 service ports to `ninep`.
- Formats port/type/id/ack/checksum/length fields.

Integration:
- Reached from IPv4/IPv6 protocol number 40.

Risks and notes:
- Packet type table is small and unknown types fall back to numeric strings.
