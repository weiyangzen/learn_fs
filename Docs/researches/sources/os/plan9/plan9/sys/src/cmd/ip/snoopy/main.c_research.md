# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/main.c

Main program for the `snoopy` packet sniffer.

Key behavior:
- Parses options for pcap/trace output, filter expression, root protocol, packet byte limit, promiscuous mode, trace input/output, checksum flag, and compact printing.
- Opens live Ethernet, IP interface snoop, trace file, or arbitrary file input.
- Builds protocol graph by resolving each module’s mux table to `Proto*`, creating dump-like placeholder protocols for unknown names.
- Compiles filter AST:
  - Completes omitted intermediate protocols via graph search.
  - Optimizes repeated protocol nodes and constant cases.
  - Calls protocol-specific compile hooks.
  - Rejects filters whose top-level protocol does not match the root.
- Applies filters by walking packet state through protocol filter callbacks.
- Prints decoded packets by repeatedly calling protocol `seprint` callbacks until no next protocol remains.
- Writes Plan 9 trace or pcap output when requested.

Integration:
- Central coordinator for every `snoopy` protocol module.
- Uses `filter.y` parser, `protos.h` protocol list, and Plan 9 network devices.

Risks and notes:
- Allocates packet buffer then shifts by 16 bytes without retaining original malloc pointer.
- Filter walk mutates `Msg.ps`; boolean branches copy state only for selected operators.
- Pcap timestamp structure uses a single `uvlong ts`, not the conventional separate sec/usec pair.
