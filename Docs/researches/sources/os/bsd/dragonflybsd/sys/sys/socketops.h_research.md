# File Research: sources/os/bsd/dragonflybsd/sys/sys/socketops.h

This kernel-only header declares DragonFly socket protocol-operation wrappers, including synchronous, direct, fast, and asynchronous protocol request paths.

Key responsibilities:
- Rejects userland inclusion.
- Includes protocol switch, socket ABI, and socket kernel state headers.
- Defines inline direct calls for:
  - `so_pru_sosend()`
  - `so_pru_soreceive()`
- Declares protocol request wrappers for:
  - abort, accept, attach, bind, connect, connect2, control, detach, disconnect, listen, peeraddr, rcvd, rcvoob, sync, send, sense, shutdown, sockaddr
- Declares async variants:
  - async abort
  - async connect
  - async rcvd
  - async send
  - async rcvd reply/drop helpers
- Declares protocol control-input/control-output helpers:
  - `so_pr_ctloutput()`
  - `so_pr_ctlport()`
  - `so_pr_ctlinput()`
  - `so_pr_ctlinput_direct()`
- Defines `so_pru_senda()`:
  - uses async send if protocol has `PR_ASYNC_SEND`
  - otherwise sends synchronously

Important invariants:
- Comments state `sosend()` and `soreceive()` can block and call other `pru_usrreq` functions, so they should be called directly from process context rather than dispatched to protocol threads.
- `so_pru_senda()` assumes async send consumes/handles the mbuf path and returns 0 immediately.

Research notes:
- This file is the adapter layer between sockets and protocol switch/user request implementations in DragonFly's message-passing network stack.
