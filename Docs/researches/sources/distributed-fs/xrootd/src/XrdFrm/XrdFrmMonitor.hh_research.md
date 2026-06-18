## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMonitor.hh

Purpose: declares the XrdFrm monitor facade and event masks. It is the shared API for enabling and sending monitoring records from stage, migration, and purge code.

Important APIs/types: macros define `XROOTD_MON_INFO`, `XROOTD_MON_STAGE`, `XROOTD_MON_MIGR`, and `XROOTD_MON_PURGE`. Public static methods configure defaults, initialize identity/network state, emit identity records, and map activity records. Public static chars `monMIGR`, `monPURGE`, and `monSTAGE` are fast-path flags used by hot transfer/purge code to avoid building monitor records when disabled.

State and persistence: private static members describe two destinations, modes, `XrdNetMsg` pointers, process start time, identity buffer/length, server id string, and identity interval. This is runtime-only state.

Dependencies and integration: depends on `XrdXrootdMonData.hh` and protocol integer types. Forward declares `XrdNetMsg` so most consumers only need the header without pulling network implementation.

Risks and test signals: public writable flag chars can be mutated outside initialization, so tests should treat them as part of the ABI. Validate that `Defaults()` ownership expectations for destination strings are respected by callers and that `Init()` is not called twice without cleanup leaks.
