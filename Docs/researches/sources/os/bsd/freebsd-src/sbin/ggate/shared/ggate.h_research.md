# File Research: sources/os/bsd/freebsd-src/sbin/ggate/shared/ggate.h

`ggate.h` defines the shared userland GEOM Gate protocol and helper API.

Key definitions:
- Default TCP port, socket buffers, queue size, and timeout.
- Protocol magic string `GGATE_MAGIC`, protocol version `GGATE_VERSION`, and command codes for read, write, and flush.
- Protocol flags for read-only/write-only, send socket, receive socket, and direct I/O.
- Packed wire structs:
  - `g_gate_version`
  - `g_gate_cinit`
  - `g_gate_sinit`
  - `g_gate_hdr`
- Declarations for logging, device control, media/sector probing, socket I/O, socket tuning, provider listing, and hostname/IP resolution.
- Inline byte-order conversion helpers for all protocol structs.

Important details:
- The protocol uses big-endian/network order for multi-byte wire fields.
- The comments document the two-socket connection role: `GGATE_FLAG_SEND` and `GGATE_FLAG_RECV` distinguish the paired data channels.
- `g_gate_sinit` and `g_gate_hdr` swap only the fields that are actually used.
