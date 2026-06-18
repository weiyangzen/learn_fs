# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto.h

Read completely: 60 lines.

This header declares the public HAST protocol transport abstraction.

Key responsibilities:
- Declares opaque `struct proto_conn`.
- Declares client/server creation, connect, connect-wait, accept, send, receive, connection passing, descriptor lookup, address matching, address rendering, timeout configuration, and close functions.

Important interactions:
- Used by daemon parent/worker code, control/event channels, and HAST remote protocol framing.

Reliability notes:
- The API hides backend details, but callers must respect connection side semantics and close every returned `proto_conn`.
