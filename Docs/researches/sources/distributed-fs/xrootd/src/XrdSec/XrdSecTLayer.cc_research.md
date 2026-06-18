# sources/distributed-fs/xrootd/src/XrdSec/XrdSecTLayer.cc

Purpose: Implements a transport-layer shim for security protocols that need socket-style handshakes over the XRootD authentication exchange.

Important APIs and functions: `getCredentials` drives the client side; `Authenticate` drives the server side; `bootUp` creates a socketpair and starts the protocol thread; `Read` self-paces socket reads; `secDone`, `secDrain`, `secError`, and `secXeq` handle completion, thread/socket cleanup, and error propagation.

Control flow: On first use, the wrapper creates a UNIX socketpair, starts a thread running derived `secClient` or `secServer`, and exchanges framed `TLayerRR` records as credentials/parameters. Each frame carries protocol name, `xfrData` or `endData`, and optional bytes. Reads poll in short slices and switch to `endData` after repeated no-progress slices. Final completion drains the socket, waits for the thread semaphore, and returns success or error.

State and persistence: Per object state includes thread id, semaphore, initiator/responder roles, socket fds, time-slice counters, error code/text, and reusable header. No durable state exists.

Dependencies and integration points: Uses `XrdSecProtocol`, `XrdOucErrInfo`, `XrdSysThread`, `XrdSysSemaphore`, `XrdSysFD_Socketpair`, `poll`, `read`, `write`, and derived protocol implementations such as TLS-like mechanisms.

Risks: Derived `Delete` must join `secTid`; otherwise thread lifecycle is unsafe. The framing header carries only an eight-byte protocol name and minimal validation. Timeouts are CPU/poll-slice based rather than wall-clock RTT. `write` does not handle partial writes. `eDest` is a raw pointer set from the current call.

Test signals: Derived fake client/server that exchange multiple frames, server-initiated and client-initiated starts, partial/no-progress reads, invalid frame sizes/codes, socketpair/thread creation failure injection, error propagation, and deletion while a thread is active.
