# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFileSystem.hh

## Purpose
Declares `XrdOssStats::FileSystem`, an `XrdOssWrapper` implementation that owns an underlying OSS and records operation counts/timings.

## Important APIs and types
Public APIs include construction, `Config()`, `InitSuccessful()`, `newDir()`, `newFile()`, and overrides for filesystem operations that can be instrumented. Private `AggregateBootstrap()` and `AggregateStats()` drive periodic emission. Nested `OpTimer` records count and elapsed time via RAII. `OpRecord` groups operation counters; `OpTiming` groups accumulated nanosecond timers.

## State, dependencies, and integration
The class is friends with `File` and `Directory`, allowing descriptor wrappers to update counters directly. It stores `m_gstream`, initialization state, `m_runmode`, owned `m_oss`, environment pointer, logger, normal/slow counters, normal/slow timings, and slow-duration threshold. Dependencies are `XrdOssWrapper`, `XrdSysError`, `XrdSysRAtomic`, and `XrdXrootdGStream` forward declaration.

## Risks and test signals
All counters are atomic, but object lifetime around the background thread is the main concurrency risk. The header exposes many counters indirectly through friendship, so changes to counter names must stay synchronized with JSON output. Tests should compile wrappers against the current OSS virtual method set and verify ABI/plugin loading.
