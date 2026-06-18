# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFile.cc

Purpose: implements the SFS file wrapper that enforces load shedding, bandwidth/IOPS throttling, concurrency throttling, and open-file accounting around data operations.

Important APIs/types/functions: `File::open()`, `close()`, `fctl()`, `getMmap()`, read/write/paged/AIO variants, `SendData()`, and pass-through methods for checkpoint/sync/stat/truncate/checksum info. Macros `DO_LOADSHED` and `DO_THROTTLE` centralize pre-I/O checks.

Control flow: `open()` maps client identity to user/UID, prepares load-shed opaque data, calls `OpenFile()`, delegates to underlying SFS open, and rolls back accounting on failure. `close()` clears `m_is_open`, closes accounting, and delegates close. Data-transfer methods execute load-shed check, apply share throttling, start an I/O timer, fail with `SFS_ERROR`/`EMFILE` when concurrency wait times out, then call the wrapped operation. AIO methods perform synchronous wrapped calls and immediately complete callbacks.

State and persistence: per-file state includes open flag, wrapped SFS file, user identity, hashed UID, prepared load-shed opaque string, connection ID, and references to throttle manager/error route. Open counters persist in the manager until `close()` or destructor rollback.

Dependencies and integration: depends on `XrdSfsAio`, security entity attributes, and `XrdThrottle.hh`. It is created by `FileSystem::newFile()`.

Risks: macros rely on member names and local `error`, making control flow hard to audit. Destructor rolls back only if `m_is_open`, so any accounting mismatch outside normal open/close can persist. AIO is no longer asynchronous. Disabling `SFS_FCTL_GETFD` and mmap can reduce performance or change client behavior.

Test signals: open success/failure accounting, close idempotence, all throttled I/O paths, load-shed redirect, max wait timeout mapping to `EMFILE`, AIO completion, and pass-through metadata methods.
