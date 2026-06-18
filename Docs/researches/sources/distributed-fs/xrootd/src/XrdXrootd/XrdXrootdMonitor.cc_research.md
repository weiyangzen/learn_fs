# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonitor.cc

Purpose: implements the central XRootD monitoring subsystem for user/info/path dictionaries, I/O trace packets, file-event duplication, redirect monitoring, identity announcements, clock windows, and destination routing.

Important APIs/types/functions: `Defaults()` overloads configure modes, sizes, intervals, and destinations; `Init()` overloads construct server identity and initialize destinations; `Alloc()`/`unAlloc()` manage per-user monitors; `User::Register`, `Enable`, `Disable`, and `Report` handle monitor users; event methods `Open`, `Close`, `Disc`, `appID`, `Map`, `Redirect`, `Tick`, `Send`, `Flush`, and `Mark` emit packets. Nested `Hello` registers generic-stream identity callbacks.

Control flow: startup calls `Defaults()` then `Init(sp,errp,host,prog,name,port)` to build SID/identity strings, and later `Init()` to open destinations, schedule identity jobs, allocate alternate file-only monitor, start the clock, initialize fstat, and allocate redirect buffers. Runtime users call `Register()` to obtain monitor identity and optionally an `Agent`. I/O events append trace entries to per-agent buffers, inserting window marks or flushing when windows/buffers roll. `Tick()` advances the global window, flushes alt/redirect buffers as needed, and stops in selective mode when no monitors remain. `Send()` routes packets to up to two destinations based on mode masks with independent packet sequences.

State and persistence behavior: extensive static process state: destinations and sockets, monitor mode flags, identity record/string variants, SID, current window, buffer sizes, redirect buffer ring, alt monitor, counters, and scheduler pointers. Per-agent state includes a monitor buffer, next-entry cursor, and last-window marker. Persistence is monitor UDP traffic and environment export `XRDMONRDR` when redirect monitoring is active.

Dependencies: `XrdNetMsg`, `XrdOucEnv`, `XrdOucUtils`, `XrdScheduler`, `XrdSysError`, `XrdXrootdMonData`, `XrdXrootdMonFile`, `XrdXrootdTrace`, `XrdSecMonitor`, platform byte-order helpers, and `XrdVersion`.

Integration points: used throughout xrootd request/file/session handling, by security monitor reporting through `XrdSecMonitor`, by redirect paths, by generic G-Stream identity hails, and by fstat monitoring.

Risks: this is global, mutable, and timing-sensitive. Selective-mode clock start/stop depends on `numMonitor`; sequence numbers are per destination under a send mutex; I/O event paths intentionally avoid heavy locking and rely on atomic-enough simple memory reads. `Map()` copies user name plus path into a fixed `info` buffer and must rely on bounded path copy. Redirect buffers use a shared free ring and per-buffer locks. `User::Register()` allocates `Name` without clearing any previous value, so object reuse must call `Clear()` first.

Test signals: one and two destination routing masks; identity record content and periodic schedule; monitor disabled, all, and selective modes; map user/path/info/token packets; I/O open/read/write/readv/close/disc trace ordering; auto-flash/auto-flush windows; redirect record truncation and buffer flushing; fstat init failure; alt monitor duplication for file/user modes.
