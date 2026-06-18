## sources/distributed-fs/xrootd/src/Xrd/XrdMain.cc

Purpose: provides the xrootd server entry point, early process setup, configuration, listener thread creation, and accept-loop scheduling.

Important APIs/types/functions: local class `XrdMain` is an `XrdJob` whose `DoIt()` accepts a connection and assigns the protocol loader. `mainAccept()` creates an `XrdProtLoad` for a port and continuously schedules accept jobs, waiting on a semaphore after each accept. `mainAdmin()` contains placeholder admin accept handling. `main()` sets timezone/signal/thread defaults, configures the server, starts admin and extra port accept threads, and runs the primary accept loop.

Control flow: process startup blocks signals, lowers default stack size, calls `XrdConfig::Configure`, then spawns one accept thread per configured network beyond the first. Each accept job calls `XrdInet::Accept()`; accepted links receive `XrdProtLoad` and immediately run `setProtocol(..., true)`.

State/persistence: startup state is in `XrdMain::Config` and per-thread `XrdMain` instances. No persistent storage is written here.

Dependencies/integration: integrates with `XrdConfig`, `XrdInet`, `XrdLink`, `XrdProtLoad`, `XrdScheduler`, `XrdSysThread`, and `XrdSysUtils`.

Risks: `mainAccept()` constructs `XrdProtLoad ProtSelect` on the accept thread stack and stores its address in `Parms->theProt`; this is valid only because the function loops forever. Admin handling is explicitly superfluous and uses an `int` cast as protocol placeholder, so enabling it without real implementation would be unsafe. The process exits with `_exit()` on configuration/thread failures.

Test signals: server smoke tests should verify config parsing, multi-port accept startup, TLS and non-TLS protocol matching per port, signal blocking, and behavior when admin network is configured.
