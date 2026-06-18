## sources/distributed-fs/xrootd/src/XrdNet/XrdNetMsg.cc

Purpose: Implements UDP-style message sending to a default or per-call endpoint, with optional send readiness timeout and address refresh registration.

Important APIs and functions: Constructor, destructor, three `Send` overloads, `OK2Send`, and `retErr` helpers are implemented.

Control flow: Construction creates a UDP relay socket through `XrdNet`; with a default destination, it validates the address, connects the UDP socket, records the default destination string/fd, and optionally registers with `XrdNetRefresh`. `Send` with no destination uses connected `send`; with a destination uses `sendto`; with iovec uses `writev` for connected sockets or `sendmsg` for explicit destinations. `OK2Send` polls for writability when a nonnegative timeout is requested. Errors are logged and mapped to `-1` or positive timeout/block indicators.

State and persistence: Stores logger pointer, duplicated default destination, fd, `destOK`, and `isRefr`. No persistent state; address refresh registration is process-local.

Dependencies and integration points: Uses `XrdNet`, `XrdNetAddr`, `XrdNetPeer`, `XrdNetRefresh`, `XrdSysError`, POSIX `send`, `sendto`, `sendmsg`, `writev`, and `poll`. Used by CMS notification and other local datagram signaling.

Risks: Constructor registers refresh but never sets `isRefr = true`, so destructor will not unregister. If construction with a bad non-null destination returns early, `FD` may remain `-1` and `dfltDest` null; destructor still calls `close(FD)` and logs using possibly null destination. Timeout argument is documented as milliseconds and passed directly to `poll`; other networking APIs use seconds, so caller confusion is possible. `Send` with explicit destination requires same family as socket but only discovers mismatch at send time.

Test signals: Construct with null, valid, invalid, and refresh-enabled destinations; send default, explicit string, sockaddr, and iovec messages; simulate blocked socket, `EAGAIN`, fatal errors, and destructor after constructor failure; verify refresh unregister behavior.
