# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoemd.c

`snoopy` decoder for AoE mask directive entries.

Key behavior:
- Parses reserved byte, edit command, and Ethernet address.
- Filters on command or Ethernet address.
- Formats command with textual edit marker and Ethernet address.

Integration:
- Reached from `aoemask.c`.

Risks and notes:
- Ethernet address filter treats configured value as numeric `ulv`, which is awkward for 48-bit addresses.
