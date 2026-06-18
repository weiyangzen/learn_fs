## sources/distributed-fs/xrootd/src/XrdNet/XrdNetConnect.hh

Purpose: Declares the static `XrdNetConnect` utility for timeout-capable socket connects.

Important APIs and types: Public static `Connect(int fd, const sockaddr *name, int namelen, int tsec=-1)` returns zero on success or errno on failure. Constructor/destructor are private to prevent instances.

Control flow: Header documents syscall-compatible semantics plus optional timeout behavior.

State and persistence: Stateless utility class; no persistence.

Dependencies and integration points: Includes platform socket headers and is consumed by `XrdNetSocket` or other low-level connection code.

Risks: Timeout unit is seconds in declaration comments but implementation passes milliseconds to `poll` after multiplying by 1000. Default `-1` means wait indefinitely in implementation, not "no timeout" in the `tsec == 0` branch.

Test signals: Compile on POSIX and Windows-gated builds; verify default timeout semantics match all callers' expectations.
