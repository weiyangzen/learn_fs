<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixStats.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixStats.hh

Purpose: Defines a small thread-safe statistics accumulator for the POSIX facade. It currently tracks open/close counts and errors and is used by the XRootD POSIX client layer and config stats reporting.

Important APIs/types/functions: `PosixStats` contains `Opens`, `OpenErrs`, `Closes`, and `CloseErrs`. `Get()` snapshots counters into another `XrdPosixStats`. `Add()`, `Count()`, and `Set()` update counters under `sMutex`; `Count()` uses XrdSys atomic macros while holding the mutex. `Lock()` and `UnLock()` expose coarse locking for external grouped operations.

Control flow and state: State is process-local and in-memory. Construction zeroes the counter struct with `memset`. There is no persistent storage and no automatic export here; callers must ask for or format stats elsewhere.

Dependencies/integration: `XrdPosixGlobals::Stats` is defined in `XrdPosixXrootd.cc` and incremented during open/deferred-open error paths. PSS exposes stats through `XrdPssSys::Stats()` via `XrdPosixConfig::Stats("pss", ...)`.

Risks and test signals: Counter coverage is limited; increments are easy to miss when new open/close paths are added. Tests should verify concurrent increments, snapshot consistency, stats text output from PSS/POSIX config, and error-path increments for normal open, deferred open, and close failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixStats.hh -->
