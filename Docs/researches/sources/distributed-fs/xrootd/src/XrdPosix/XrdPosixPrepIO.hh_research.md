<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.hh

Purpose: Declares `XrdPosixPrepIO`, an `XrdOucCacheIO` implementation that fronts a not-yet-opened `XrdPosixFile`. It exposes the cache I/O interface while deferring the real XRootD open until a method needs file metadata or bytes.

Important APIs/types/functions: Inline methods implement `Fcntl`, `FSize`, `Fstat`, `Open`, `Read`, async `Read`, `ReadV`, async `ReadV`, `Sync`, async `Sync`, `Trunc`, `Write`, and async `Write`. Each calls private `Init()` and then delegates to `fileP`, or returns/completes with `openRC` if initialization failed. `Detach()` always returns true. `Path()` forwards to `fileP->Path()`. `Disable()` is implemented in the `.cc`.

Control flow and state: The object stores `fileP`, `openRC`, `iCalls`, and the XRootD open flags/mode needed by lazy open. There is no owned persistence beyond the backing file object; it is a transitional object updated into the real file cache I/O once opening succeeds.

Dependencies/integration: Depends on `XrdOucCacheIO`, `XrdPosixFile`, and XrdCl open flag/access enums. Used by `XrdPosixXrootd::Open()` when cache prepare returns a positive deferral signal.

Risks and test signals: Because most behavior is inline, ABI and include dependencies matter. Tests should cover every forwarded operation both before and after successful lazy open, failure propagation to sync and async APIs, cache detach interactions, and preservation of the original open flags and access mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPrepIO.hh -->
