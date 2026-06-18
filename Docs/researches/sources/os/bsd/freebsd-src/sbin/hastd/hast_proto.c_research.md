# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_proto.c

`hast_proto.c` implements the HAST message framing layer over generic proto connections.

Key behavior:
- Defines a packed main header containing protocol version and serialized nv header size.
- Defines a send/receive pipeline with stages:
  - compression
  - checksum
- `hast_proto_send()`:
  - Optionally runs outgoing data through compression then checksum.
  - Adds final payload `size` to nv metadata.
  - Serializes nv to an `ebuf`.
  - Prepends main header.
  - Sends header/nv bytes, then payload bytes if present.
- `hast_proto_recv_hdr()`:
  - Receives main header.
  - Rejects versions newer than supported with `ERPCMISMATCH`.
  - Allocates an ebuf for nv bytes, receives them, and deserializes nv.
- `hast_proto_recv_data()`:
  - Reads payload size from nv.
  - Receives the encoded payload.
  - Runs receive pipeline in reverse order: checksum verification, then decompression.
  - Copies decoded data into caller-provided buffer if pipeline allocated a replacement buffer.
  - Rejects decoded data larger than caller capacity.

Important details:
- Header size is little-endian on wire.
- When `res` is NULL, send uses the current maximum protocol version.
- The pipeline ignores send-stage return values in `hast_proto_send()`, so stages signal hard nv errors through later `nv_error()` checks or errno paths only when visible.
