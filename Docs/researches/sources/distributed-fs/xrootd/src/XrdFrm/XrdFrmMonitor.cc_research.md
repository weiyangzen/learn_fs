## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMonitor.cc

Purpose: implements XrdFrm monitoring event emission for info, stage, migration, and purge activity. It builds XRootD monitor map packets and sends them to up to two configured collectors.

Important APIs and control flow: `Defaults()` accepts strdup-owned destination strings plus mode masks, normalizes empty destination/mode combinations, and sets `monMIGR`, `monPURGE`, and `monSTAGE` feature flags. `Init()` creates a server identity via `XrdOucUtils::Ident()`, constructs an identification record, opens `XrdNetMsg` destinations, and optionally starts a periodic `Ident()` thread. `Map()` converts user/path data into `XrdXrootdMonMap`, handles special transfer event codes, fills a header, and routes the packet through `Send()`. `fillHeader()` assigns sequence bytes under a mutex.

State and persistence: all monitor state is process-global static memory: destination strings, `XrdNetMsg` objects, identity record, sequence counter, start time, and event-mode booleans. No durable state is written.

Dependencies and integration: transfer and purge paths call `XrdFrmMonitor::Map()` when monitor flags are enabled. It uses `XrdXrootdMonData` packet layouts, `XrdNetMsg` network delivery, `XrdSysThread`, and global `Say` logging.

Risks and test signals: `Map()` copies username and path into fixed buffers; long inputs require bounds-sensitive tests. `Send(-1, ...)` in `Ident()` intentionally targets any destination whose mode intersects `-1`, but this bitmask idiom should be tested. Initialization failure messages include an unused `etext` pointer. Tests should verify mode routing, sequence wrap, dual collectors, identity record length, and thread startup failure handling.
