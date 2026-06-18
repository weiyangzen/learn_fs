# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/main.c

Interactive ATA command shell and diagnostic tool.

Important behavior:
- Opens `/dev/.../raw`, reads device signature and identify data, and stores geometry, sector size, flags, and WWN.
- `issueata`, `issuepkt`, and `issuesct` implement ordinary ATA passthrough, ATAPI inquiry, and SCT command sequencing.
- Provides formatting for identify data, raw I/O data, SMART data/status, SMART logs, SCT status, log page maps, SATA PHY events, and queued page counters.
- Command parser supports named ATA commands, register assignment, SCT feature tables, redirection, command tracing, open/close/probe/help/rfis/dev special commands, and interrupt handling.
- Maintains reusable `Req` state for LBA, sector count, data buffers, raw output, and redirection file descriptors.

This is low-level and can issue destructive ATA writes; command metadata in `tabs.h` determines protocols and formatting.
