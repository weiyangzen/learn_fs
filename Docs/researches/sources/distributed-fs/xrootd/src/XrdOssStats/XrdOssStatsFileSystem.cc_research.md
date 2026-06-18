# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFileSystem.cc

## Purpose
Implements the stats OSS wrapper that instruments filesystem operations and periodically emits aggregate metrics through XRootD's monitoring g-stream.

## Important APIs and control flow
The constructor configures logging and slow-operation threshold, obtains `oss.gStream*` from the environment, reads optional `oss.runmode`, starts a background aggregation thread with `XrdSysThread::Run()`, and marks the wrapper ready. Missing g-stream is treated as non-fatal bypass; missing environment and thread creation failures are fatal. `InitSuccessful()` communicates those outcomes and releases ownership of the underlying OSS on bypass.

`Config()` gathers `fsstats.trace` and `fsstats.slowop` directives from the config file. It maps trace names to `XrdSysError` masks and parses slow durations with `ParseDuration()`. `newDir()` and `newFile()` wrap underlying descriptors in stats `Directory` and `File` objects. Filesystem operations such as `Chmod`, `Rename`, stat variants, `Truncate`, and `Unlink` are timed with `OpTimer`.

`AggregateBootstrap()` loops forever, sleeping one second and calling `AggregateStats()`. `AggregateStats()` formats one JSON record with normal and slow counts plus accumulated seconds and inserts it into g-stream. `OpTimer` increments counts and nanosecond totals on destruction, including separate slow counters when duration exceeds the configured threshold.

## State, dependencies, and integration
State is atomic counter structs, timing structs, `m_slow_duration`, `m_runmode`, owned wrapped OSS, logger, and g-stream pointer. Dependencies include `XrdOucGatherConf`, `XrdOssWrapper`, `XrdXrootdGStream`, atomics, pthread helpers, and `<thread>`.

## Risks and test signals
The aggregation thread has no shutdown path and may call into a destructing object if plugin lifetime changes. JSON formatting uses a fixed 1500-byte buffer. Tests should validate config parsing, startup bypass/fatal cases, metric increments for all wrapper methods, slow thresholds, runmode event naming, and g-stream insert failure logging.
