<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.cc

## Purpose
`XrdFrmCns.cc` implements optional notifications to the CNS daemon by writing event records to an `XrdCnsd.events` FIFO/file under the configured admin path.

## Important Functions
`Add()` emits create and closew events for a path, size, and mode. `Rm()`/`Rmd()` in the header call private `Del()` with file or directory delete headers. `Init(const char*, int)` presets path/mode, while `Init(myID, aPath, iName)` constructs headers and default path. Private `Init()` lazily opens the event path. `Retry()` controls auto/require/ignore behavior on FIFO errors. `Send2Cnsd()` serializes writes with `XrdOucSxeq` and writes an iovec. `setPath()` builds and validates the event path.

## Control Flow, State, And Persistence
All state is static: `cnsPath`, delete headers, fd, mode, and initialization flag. In auto/require modes, the first send lazily opens the event path. Require mode sleeps and retries on missing/not-ready daemon; auto mode logs then disables action for that send. Event records are persistent only insofar as they are written to the CNS daemon endpoint.

## Dependencies And Integration Points
The file depends on `XrdFrmConfig` for PFN-to-LFN conversion during delete events, `XrdOucUtils::genPath()`, `XrdOucSxeq`, `XrdSysMutex`, `XrdSysTimer`, POSIX open/writev/stat, and global `Say`. Config initializes it via `frm.all.cnsd` and `ConfigPaths()`, while admin unlink and other FRM operations call `Add`, `Rm`, or `Rmd`.

## Risks And Test Signals
`Send2Cnsd()` serializes on `cnsFD`; if opening failed or fd is stale, behavior depends on retry paths. `Add()` has a fast `if (!cnsMode) return`, while `Del()` relies on callers checking mode. Require mode can block indefinitely in 10-second sleeps until CNS appears. Tests should cover ignore/auto/require modes, absent FIFO, broken pipe, PFN-to-LFN conversion failure, concurrent notifications, and event record formatting within pipe atomicity limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmCns.cc -->
