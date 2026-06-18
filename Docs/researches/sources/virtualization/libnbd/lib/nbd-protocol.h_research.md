# File Research: sources/virtualization/libnbd/lib/nbd-protocol.h

Local NBD wire protocol definitions shared by libnbd internals.

Major contents:
- Packed wire structs for old/new handshakes, newstyle options, option replies, export-name replies, requests, extended requests, simple/structured/extended replies, data/hole/block-status/error chunks.
- Magic constants for handshake, requests, and replies.
- Global flags, per-export flags, option codes, reply codes, info codes.
- Structured reply flags/types.
- Command codes and command flags.
- NBD wire error codes.

Interactions:
- `internal.h` embeds many of these structs in static buffers.
- `protocol.c` maps NBD error and command codes.
- Generated state machine reads/writes these wire layouts.

Research notes:
- All fields are network byte order; callers must use byte-swapping helpers.
- The header is BSD-licensed and notes it originated from nbdkit-style protocol definitions.
