# sources/user-network-fs/s3fs-fuse/src/s3fs_logger.cpp

Purpose: implements s3fs logging, including singleton lifecycle, syslog integration, file logging, timestamp formatting, debug-level transitions, environment overrides, and printf-style log emission.

Important APIs and functions: `S3fsLog::IsS3fsLogLevel`, `GetCurrentTime`, `SetLogfile`, `ReopenLogfile`, `SetLogLevel`, `BumpupLogLevel`, `SetTimeStamp`, constructor/destructor, `LowLoadEnv`, `LowSetLogfile`, `LowSetLogLevel`, `LowBumpupLogLevel`, `Printf`, `s3fs_low_logprn`, and `s3fs_low_logprn2`.

Control flow: constructing the singleton opens syslog and reads `S3FS_LOGFILE` and `S3FS_MSGTIMESTAMP`. Static methods delegate to the singleton for mutable operations. Log macros in the header call `s3fs_low_logprn*`, which either write atomically to stdout/stderr/logfile or send to syslog depending on foreground/logfile state. `SIGUSR2` bumps log level via `BumpupLogLevel`; `SIGHUP` reopens via `ReopenLogfile`.

State and persistence: static state holds singleton pointer, current debug level, `FILE*` logfile, logfile path, and timestamp mode. File logs persist externally. `Printf` bypasses stdio buffering and writes directly to the file descriptor, retrying on `EINTR`.

Dependencies and integration points: uses process globals `foreground` and `instance_name`, `CaseInsensitiveStringView`, syslog APIs, `clock_gettime`/`gettimeofday`, and signal handling.

Risks: `GetCurrentTime` appears to invert `clock_gettime` handling: on failure it reads `tsnow`, and on success it calls `gettimeofday`, so timestamp behavior deserves correction/testing. `ReopenLogfile` appears to reject non-empty `logfile`, which conflicts with its purpose and likely breaks SIGHUP log rotation. Static logger state is not mutex-protected, so concurrent logfile changes and logging can race. Formatting code computes `vsnprintf` lengths without checking negative values in `s3fs_low_logprn*`.

Test signals: tests for `S3FS_LOGFILE`, `S3FS_MSGTIMESTAMP`, log-level masks, foreground/syslog branching, SIGHUP reopen, SIGUSR2 level cycling, concurrent logging line integrity, and timestamp sanity under successful `clock_gettime`.
