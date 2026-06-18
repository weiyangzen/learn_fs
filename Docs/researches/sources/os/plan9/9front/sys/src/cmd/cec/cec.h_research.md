# File Research: sources/os/plan9/9front/sys/src/cmd/cec/cec.h

Shared CEC protocol and helper declarations.

Key definitions:
- `Pkt` defines Ethernet destination/source, EtherType, CEC type/connection/sequence/length, and data payload.
- Multiplexer message types: `Fkbd`, `Fcec`, `Ffatal`.
- Protocol constants: `Iowait` and custom `Etype`.
- Declares opaque `Mux` and functions for muxing, network I/O, dumping packets, raw console mode, and exit cleanup.
- Exposes global `debug`.

Dependencies:
- Consumed by `cec.c`, `mux.c`, `plan9.c`, and `utils.c`.

Research notes:
- The packet layout is fixed around raw Ethernet frames.
