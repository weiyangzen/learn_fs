# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgramdump.c

Debug printer for decoded NetBIOS datagrams.

Key behavior:
- Prints type, flags, id, source IP, and source port.
- For error packets, prints error code.
- For data packets, prints datagram length, offset, source name, and destination name.

Interactions:
- Uses `%I` IP formatter and `%B` NetBIOS name formatter.

Notable details:
- Does not dump datagram payload bytes; raw data dumping is handled by `nbdumpdata`.
