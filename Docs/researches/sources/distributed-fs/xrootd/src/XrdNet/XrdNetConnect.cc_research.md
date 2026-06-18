## sources/distributed-fs/xrootd/src/XrdNet/XrdNetConnect.cc

Purpose: Implements a static connect wrapper that can apply a caller-specified timeout without using process-wide alarms.

Important APIs and functions: `XrdNetConnect::Connect` accepts an fd, sockaddr, address length, and timeout seconds, returning zero or errno.

Control flow: With `tsec == 0`, it calls blocking `connect`. Otherwise it saves flags, sets non-blocking mode, calls `connect`, handles immediate success or non-`EINPROGRESS` error, polls for writability until timeout, reads `SO_ERROR`, restores flags, and returns the result.

State and persistence: No object state and no persistence; all state is local to the call and the socket fd flags.

Dependencies and integration points: Uses `fcntl`, `connect`, `poll`, `getsockopt`, socket headers, and `XrdSysPlatform` for platform errno/data macros. Called by lower-level socket connection setup.

Risks: The final restore call uses `F_SETFD` instead of `F_SETFL`, so file status flags may not be restored as intended. Negative `tsec` still enters timeout path and passes a negative poll timeout, effectively waiting indefinitely after changing to non-blocking. It does not check `fcntl` failures.

Test signals: Immediate connect, refused connect, in-progress success, timeout, interrupted poll, negative timeout, and flag restoration on sockets with preexisting nonblocking/other status flags.
