# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/vlan.c

This snoopy module decodes IEEE 802.1Q VLAN headers.

Key behavior:
- Parses 16-bit tag and 16-bit encapsulated EtherType.
- Filters support VLAN ID (`v`), priority (`q`), and type (`t`).
- Reuses external `ethertypes[]` for subprotocol demux and filter compilation.
- Prints VLAN ID, queue priority, EtherType, and packet length.
- Demuxes to the EtherType-selected protocol or `dump`.

Research notes:
- The priority is taken from the upper four bits of the tag, although VLAN priority is usually three bits plus CFI/DEI.
