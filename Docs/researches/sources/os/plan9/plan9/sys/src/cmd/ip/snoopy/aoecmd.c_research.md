# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoecmd.c

`snoopy` decoder for AoE config command payloads.

Key behavior:
- Parses buffer count, firmware version, sector count, config command/version nibble, and config string length.
- Filters on low-nibble config command.
- Formats fields and prints the config string payload.

Integration:
- Selected by `aoe.c` command demux value `1`.

Risks and notes:
- Prints `len` bytes from packet payload without independently clamping to remaining packet size.
