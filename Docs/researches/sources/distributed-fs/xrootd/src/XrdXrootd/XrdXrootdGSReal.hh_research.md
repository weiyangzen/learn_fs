# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGSReal.hh

Purpose: declares the real G-Stream implementation that combines `XrdJob` scheduling, public `XrdXrootdGStream` insertion APIs, and `XrdXrootdMonitor::Hello` identity reporting.

Important APIs/types/functions: public stream methods mirror the facade: `Flush`, `GetDictID`, `HasHdr`, `Ident`, `Insert`, `Reserve`, `SetAutoFlush`, `GetAutoFlush`, and `Space`. `GSParms` defines plugin name, destination, monitor mode, max packet length, flush interval, stream type, options, format, and header detail. Format constants include `fmtNone`, `fmtBin`, `fmtCgi`, `fmtJson`; header constants range from `hdrNone` to `hdrFull`.

Control flow: callers instantiate this class with validated monitor options, then pass its base `XrdXrootdGStream` reference to plugins. Scheduler calls `DoIt()` for auto-flush. The `Hello` base calls `Ident()` during monitor hails.

State and persistence behavior: owns process-resident packet buffers, header strings, sequence counters, timestamp fields, reservation state, destination socket object, and monitor user identity. No durable data is kept; all persistence is monitor packets sent externally.

Dependencies: `XrdJob`, `XrdSysPthread`, `XrdXrootdGStream`, `XrdXrootdMonData`, `XrdXrootdMonitor`, and forward-declared `XrdNetMsg`/`XrdSysError`.

Integration points: created by monitor configuration for generic stream modes and consumed by internal/external plugins that need structured monitoring output.

Risks: destructor intentionally does not free several allocated buffers because these objects are normally process-lifetime; tests that create many instances may leak unless isolated. The private state is tightly coupled to implementation assumptions about packet layout and header placeholders. Recursive locking plus external plugin writes must be handled carefully.

Test signals: construction with every format/header pair, max-length clamping, `optNoID`, `HasHdr()` results, `Space()` after inserts and flushes, auto-flush scheduling state, and identity hail behavior.
