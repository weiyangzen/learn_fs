# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_proto.h

`hast_proto.h` declares the HAST protocol framing API.

Key API:
- `hast_proto_send()` sends an nv header and optional payload over a proto connection.
- `hast_proto_recv_hdr()` receives and deserializes the nv header.
- `hast_proto_recv_data()` receives and decodes payload data associated with an nv header.

This header is used by `hastctl`, parent/worker control, events, and primary/secondary replication code.
