# File Research: sources/os/plan9/9front/sys/src/cmd/ip/udpecho.c

This is a minimal UDP echo service.

Key behavior:
- Announces `udp!*!echo` on a configurable network mount point.
- Enables UDP header mode on the control file.
- Opens the data file read/write and writes every received packet back unchanged.
- Supports `-x netmtpt`.

Research notes:
- Because header mode is enabled, echoing the entire received buffer preserves the remote address header.
