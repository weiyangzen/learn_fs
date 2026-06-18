# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGSReal.cc

Purpose: implements the concrete generic monitoring stream, or G-Stream, used by plugins to emit monitoring records in binary, CGI, or JSON form to either a private UDP destination or the normal xrootd monitor routing layer.

Important APIs/types/functions: constructor `XrdXrootdGSReal(GSParms,bool&)`, `Flush()`, `GetDictID()`, `HasHdr()`, `Ident()`, `Insert()` overloads, `Reserve()`, `SetAutoFlush()`, `GetAutoFlush()`, and `Space()`. Private helpers `AutoFlush()`, `Expel()`, `hdrBIN()`, `hdrCGI()`, and `hdrJSN()` manage scheduled flushing and header formatting.

Control flow: construction clamps and aligns the UDP buffer size, formats an optional monitor header, creates an `XrdNetMsg` for per-stream destinations, configures autoflush, and registers a synthetic monitor user. `Insert(data,dlen)` validates a null-terminated payload, flushes if the next record will not fit, copies the record with newline termination, timestamps the packet window, and advances the buffer. `Reserve()` locks the stream and returns writable space; `Insert(dlen)` validates the reserved data, normalizes the recursive lock, timestamps, and releases. `DoIt()` is scheduler-driven and flushes aged non-empty packets before rescheduling.

State and persistence behavior: state is in memory: aligned UDP buffer pointers, packet sequence counters for data/identity/dictionary packets, timestamp window, reserved-byte flag, auto-flush state, header substitution pointers, optional `XrdNetMsg`, and registered monitor user. Persistence is only emitted UDP monitor traffic.

Dependencies: `XrdScheduler`, `XrdNetMsg`, `XrdSysRecMutex`, monitor globals in `XrdXrootdMonInfo`, `XrdXrootdMonitor`, and `XrdXrootdMonData` structures. It uses `posix_memalign`, `iovec`, network byte-order helpers, and legacy `index()`.

Integration points: backs the public `XrdXrootdGStream` facade and the `XrdXrootdMonitor::Hello` identity hail list. Plugins such as cache, TCP, TPC, throttle, OSS, and HTTP monitoring can reserve/insert payloads through the facade.

Risks: `GetDictID()` sends text dictionary records through `udpDest` without a null check after checking only `dictHdr`; header-enabled streams without a private destination need scrutiny. Reservation holds the recursive mutex across plugin code until `Insert()`, so missing completion can block all stream producers. Text headers rely on fixed placeholder locations and buffer size assumptions. `SetAutoFlush()` here accepts any positive value, while the facade clamps values below 60 seconds.

Test signals: binary/CGI/JSON header generation; hdrNone behavior; dictionary map path/info emission; identity suppression via `optNoID`; reserve/insert cancellation (`dlen == 0`); packet flush on size boundary; auto-flush scheduler firing; stream with and without private destination; invalid lengths and non-null-terminated payloads.
