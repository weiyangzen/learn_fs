# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/main.c

This is the main driver for `snoopy`, the Plan 9 network sniffer. It parses CLI flags, selects the capture source, initializes protocol formatters, builds the generated protocol graph, compiles optional filter expressions, then either prints decoded packets or emits Plan 9 trace / pcap output.

Key behavior:
- Supports live capture from ether and ipifc snoop files, or trace replay with `-t`.
- Uses `Proto` objects from generated `protos.c/protos.h` and per-protocol `mux` tables to walk packet layers.
- Implements filter evaluation, graph path completion, protocol-specific filter compilation, and simple tree optimization.
- Handles pcap headers/records with nanosecond timestamps and Plan 9 trace format.
- Provides protocol/filter help via `-?`, piping long output through `/bin/mc`.

Research notes:
- `mkfile` generates `protos.h` and `protos.c` from the `PROTOS` list; `protos.h` is not checked in.
- Filter completion assumes protocol reachability from `root`; unreachable filters become fatal internal errors.
- `parseba()` accepts exactly 16 hex bytes, despite storage room for larger arrays.
