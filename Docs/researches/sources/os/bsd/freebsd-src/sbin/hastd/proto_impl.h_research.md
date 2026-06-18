# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_impl.h

Read completely: 78 lines.

This internal header defines the protocol backend interface.

Key responsibilities:
- Defines the constructor attribute used by backend modules.
- Declares backend callback typedefs for client/server setup, connect, accept, wrapping inherited descriptors, send/receive, descriptor lookup, address matching/rendering, and close.
- Defines `struct proto`, including backend name, callback table, and queue linkage.
- Declares `proto_register()`.
- Declares shared `proto_common_send()` and `proto_common_recv()`.

Important interactions:
- Included by `proto.c`, `proto_tcp.c`, `proto_socketpair.c`, and `proto_common.c`.

Reliability notes:
- This is a private ABI between the registry and backends; callback signature mismatches or missing callbacks surface as assertions in `proto.c`.
