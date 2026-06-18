# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsConfig.cc

## Purpose
Implements stats-plugin configuration helpers and the plugin entry point used by XRootD to wrap an existing OSS.

## Important APIs and control flow
`LogMaskToString()` renders configured log mask bits as a comma-separated string, with `all` as a special case. `ParseDuration()` parses compound duration strings such as `1s500ms`; it repeatedly consumes a floating-point value and a unit among `ns`, `us`, `ms`, `s`, `m`, or `h`, rejects empty, negative, unknown-unit, missing-unit, and out-of-range inputs, and returns a `steady_clock::duration`.

The `extern "C"` function `XrdOssAddStorageSystem2()` constructs `XrdOssStats::FileSystem` around `curr_oss`, asks `InitSuccessful()` whether initialization succeeded, and either returns the new wrapper, bypasses the wrapper for non-fatal initialization failure, or returns null for fatal initialization failure. `XrdVERSIONINFO` publishes plugin version metadata.

## State, dependencies, and integration
This file depends on `XrdVersion.hh`, `XrdSysError`, and `XrdOssStatsFileSystem`. It is the integration boundary between XRootD's plugin loader and the stats filesystem wrapper.

## Risks and test signals
Parsing uses `typeof(dur)`, which is a GNU extension and may affect portability. The entry point must not delete `curr_oss` when bypassing; `InitSuccessful()` handles ownership release. Tests should exercise duration parsing edge cases and plugin startup paths for configured g-stream, missing g-stream, and fatal configuration errors.
