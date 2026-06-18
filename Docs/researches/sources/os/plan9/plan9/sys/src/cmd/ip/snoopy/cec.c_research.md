# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/cec.c

`snoopy` decoder for CEC packets.

Key behavior:
- Parses type, connection, sequence, and length.
- Filters on those fields.
- Formats type name and payload string.

Integration:
- Reached from Ethernet EtherType `0xbcbc`.

Risks and notes:
- Filter cases for `conn`, `seq`, and `len` use assignment (`=`) instead of comparison, mutating packet fields and always returning the assigned value.
- `p_compile()` reports unknown fields under the `aoe` protocol name, likely copy/paste.
