# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFile.cc

Purpose: implements the `"f"` monitor stream for per-file open, close, disconnect, and periodic transfer-stat records.

Important APIs/types/functions: static API `Defaults()`, `Init()`, `Open()`, `Close()`, and `Disc()`; scheduled `DoIt()`; private `DoXFR()` overloads, `Flush()`, and `GetSlot()`. Static state includes the report buffer, header/TOD pointers, file-stat maps, record counters, option flags, and preformatted record sizes.

Control flow: `Defaults()` derives monitoring level and record-detail flags from configuration. `Init()` allocates the UDP report buffer, formats the stream header and initial time record, computes close/XFR record layouts, and schedules a singleton job. `Open()` assigns a dictionary ID, optionally registers the file in the active transfer map, builds an open record with optional user/path LFN, and appends it to the buffer. `Close()` deregisters active transfer monitoring, emits final byte/operation/sum-of-squares stats, and marks forced closes for disconnects. `DoIt()` periodically emits XFR records for active files when the configured counter expires, flushes any buffered records, and reschedules itself.

State and persistence behavior: all state is static and process-global. The report buffer is double-used for all producer threads under `bfMutex`; active files are tracked under `fmMutex`. Persistence is UDP monitor output via `XrdXrootdMonitor::Send(XROOTD_MON_FSTA, ...)`.

Dependencies: `XrdScheduler`, `XrdSysError`, `XrdSysPlatform`, `XrdXrootdMonData`, `XrdXrootdMonitor`, and `XrdXrootdFileStats`.

Integration points: invoked from file open/close/disconnect paths and from `XrdXrootdMonitor::Init()` when fstat monitoring is enabled. It reads counters maintained by file I/O paths.

Risks: the single shared buffer serializes all file-monitor producers and comments note double buffering would be better. `Open()` sets `MonEnt` even if XFR monitoring is disabled or insertion fails, yielding encoded negative/invalid values that must be understood by close logic. LFN records use `strncpy` with padded computed length; path length has been sized but exact termination behavior depends on padding. XFR scanning drops and reacquires `fmMutex`, so file close/free can race unless map cursors and stats lifetime are safe.

Test signals: open records with and without LFN/user/read-write flag; close records with XFR only, OPS, and SSQ; forced close on disconnect; periodic XFR only for active `xfrXeq` files; buffer flush on size boundary and time interval; high-water map shrink on close; fstat disabled path.
