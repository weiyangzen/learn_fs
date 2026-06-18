# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoe.c

`snoopy` decoder for ATA over Ethernet common header.

Key behavior:
- Parses AoE version/flags, error, major, minor, command, and tag.
- Filters on shelf, slot, or command.
- Demuxes commands to `aoeata`, `aoecmd`, `aoemask`, or `aoerr`.
- Formats header fields as version, flags, error, major.minor, command, and tag.

Integration:
- Reached from Ethernet EtherType `0x88a2`.
- Shares the common `Proto` interface.

Risks and notes:
- Filter field labels appear swapped: `shelf` maps to minor and `slot` maps to major.
