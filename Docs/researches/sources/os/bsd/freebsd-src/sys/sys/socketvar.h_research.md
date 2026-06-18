# File Research: sources/os/bsd/freebsd-src/sys/sys/socketvar.h

Kernel socket object definition and socket operation API.

Key responsibilities:
- Defines `so_gen_t`, socket accept queue state, splice state, and `struct socket`.
- `struct socket` includes locks, reference count, select state, options, state, PCB, vnet/protocol, errors, SIGIO state, credentials, MAC label, generation count, OSD, FIB/user metadata, timestamp mode, pacing, splice state, I/O locks, and dataflow/listen unions.
- Defines socket state bits, socket/listen/buffer locking macros, and helpers for choosing receive/send buffers.
- Defines socket I/O lock flags, readable/writeable tests, reference-count helpers, wakeup wrappers, and accept-filter registration macro.
- Declares core socket operations: create, bind, connect, listen, accept, receive, send, shutdown, close, reserve, wakeup, AIO, splice dispatch, upcalls, state transitions, and sockopt helpers.
- Defines exported `struct xsocket` and `xsockbuf` for sysctl/libprocstat-style socket inspection.

Important patterns:
- The locking comment is a compact map of which fields are protected by socket lock, buffer locks, listen lock, I/O locks, global lock, or protocol-specific locks.
- Listening sockets reuse the union storage for incomplete/complete accept queues instead of data buffers.
- Send and receive I/O are serialized by separate `sx` locks outside the sockbufs.
- `sorele()` avoids taking the socket lock unless the reference being dropped may be the last one.
- Wakeup macros lock the relevant sockbuf to avoid test-and-wakeup races.

Research relevance:
- Main kernel socket lifecycle and synchronization contract.
- Important for file-descriptor, VFS, FIFO, sendfile, and network interaction research.
