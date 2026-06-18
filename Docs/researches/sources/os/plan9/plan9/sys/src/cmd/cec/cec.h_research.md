# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/cec.h

This header defines shared packet, mux, and platform APIs for `cec`.

Key contents:
- `Pkt`: Ethernet-console packet layout with destination/source MACs, EtherType, packet type, connection id, sequence, length, and payload.
- Packet source type enum: `Fkbd`, `Fcec`, `Ffatal`.
- Incomplete `Mux` type and mux APIs.
- Timing and EtherType constants.
- Global `debug`.
- Network API declarations: `netopen()`, `netget()`, `netsend()`.
- Utility declarations: `dump()`, `exits0()`, `rawon()`, `rawoff()`.

Filesystem relevance:
- Indirect. Defines APIs used by code that opens Plan 9 network and console files.
