# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonitor.hh

Purpose: declares the central monitor API and configuration flags used by xrootd sessions, files, security, redirects, and G-Stream components.

Important APIs/types/functions: mode bits `XROOTD_MON_*`; fstat options `XROOTD_MON_FSLFN`, `FSOPS`, `FSSSQ`, `FSXFR`; public event methods `Add_rd`, `Add_rv`, `Add_wr`, `Open`, `Close`, `Disc`, `appID`; static configuration/utility methods `Defaults`, `Init`, `Send`, `GetDictID`, `Ident`, `ModeEnabled`, `Redirect`, `Tick`, and `Flushing`. Nested `Hello` models identity callbacks; nested `User` extends `XrdSecMonitor`.

Control flow: users register a monitor identity, use inline event helpers for hot I/O paths, and rely on private `Mark()`/`Flush()` when windows or buffers fill. Static methods configure global monitor modes before runtime use.

State and persistence behavior: declares static global state for destinations, sockets, window timing, buffer sizes, flags, identity record, redirect buffers, and alternate monitor. Per-instance state is a monitor buffer and cursors.

Dependencies: `XrdSecMonitor`, `XrdSysPthread`, `XrdXrootdMonData`, `XProtocol/XPtypes`, POSIX time/types, and `XrdNetMsg`/`XrdScheduler` forward declarations.

Integration points: the API is called by request handlers and file/session objects without needing to know destination routing. Security code can call `User::Report(WhatInfo, ...)`.

Risks: many methods assume arguments are already in network byte order. Inline hot-path methods mutate buffers directly and must match implementation invariants (`lastWindow`, `nextEnt`, `lastEnt`). The private destructor prevents ordinary stack allocation cleanup assumptions. Global configuration flags are chars/ints rather than type-safe enums.

Test signals: compile-time use of inline helpers, byte-order contract tests, monitor mode mask combinations, `User` lifecycle (`Register`, `Clear`, `Enable`, `Disable`), and redirect/fstat flag enablement.
