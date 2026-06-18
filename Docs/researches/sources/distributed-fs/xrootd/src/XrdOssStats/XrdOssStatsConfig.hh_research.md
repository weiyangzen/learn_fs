# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsConfig.hh

## Purpose
Declares small configuration utilities shared by the stats plugin.

## Important APIs and types
Inside `XrdOssStats::detail`, `LogMask` defines bit values for `Debug`, `Info`, `Warning`, `Error`, and `All`. `LogMaskToString(int mask)` converts a mask to display text. `ParseDuration()` converts a user-supplied duration string into `std::chrono::steady_clock::duration` and returns an error message on failure.

## State, dependencies, and integration
The header depends only on `<chrono>` and `<string>`. It is consumed by `XrdOssStatsConfig.cc` and `XrdOssStatsFileSystem.cc` while parsing `fsstats.trace` and `fsstats.slowop`.

## Risks and test signals
The enum values intentionally mirror the message mask used by `XrdSysError`; any change should be validated against logging behavior. Unit tests should cover mask rendering and duration parsing without needing a live OSS.
