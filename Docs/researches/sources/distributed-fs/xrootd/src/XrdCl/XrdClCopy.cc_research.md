# sources/distributed-fs/xrootd/src/XrdCl/XrdClCopy.cc

## Purpose

This file implements the `xrdcp` command-line executable. It parses `XrdCpConfig`, configures the XrdCl environment, builds `CopyProcess` jobs from source/destination arguments and options, displays progress and checksums, runs the prepared copy process, reports errors, and returns shell-compatible status codes.

## Important APIs, types, and functions

`ProgressDisplay` implements `CopyProgressHandler`. It tracks ongoing jobs, prints per-job or summary progress bars to stderr, throttles progress updates to once per second, prints source/target/additional checksums from result property lists, and uses `XrdSysRecMutex` for thread-safe updates.

Helpers include `AllOptionsSupported` for early unsupported SOCKS proxy rejection, `AppendCGI` for adding opaque CGI parameters to URLs, `ProcessCommandLineEnv` for applying `-D` environment definitions, `FileType2String`, `CountSources`, `AdjustFileInfo`, `IndexRemote` for recursive remote directory expansion, and `CleanUpResults`.

`main` is the full CLI driver: parse config, configure logging and delegation, derive booleans, parse checksum options, set environment knobs, normalize destination/source URLs, determine whether the target is a directory, optionally index remote recursive sources, build one property list per source, append a process configuration job, call `Prepare`, call `Run`, print errors, free result lists, and return `XRootDStatus::GetShellCode()` on failure.

## Control flow

After `XrdCpConfig::Config`, unsupported options abort with code 50. CLI `-D` definitions update `DefaultEnv`. Logging level and progress printing are configured, then flags such as force, POSC, TPC, ZIP append, server mode, delegation, recursion, makedir, dynamic source, xattrs, remove-on-bad-checksum, and continue are translated to local variables.

Checksum flags choose `checkSumMode`, `checkSumType`, optional preset, and progress checksum printing. Environment options set substream count, retry policy, TLS behavior, ZIP metalink checksum behavior, chunk size, xcp block size, and parallel chunk count. A scope-exit object stops PostMaster on process exit.

The destination is normalized to a URL string, including absolute `file://` conversion for local paths. Remote target `Stat` decides whether the target is a directory and catches authorization errors. Multiple sources require a directory or stdout target. Remote recursive directory sources are expanded with `DirList(Recursive|Locate|Merge)`.

For each source, the code normalizes local paths to `file://`, appends source and destination CGI, preserves recursive directory layout when needed, fills the property list keys consumed by `CopyProcess`/`ClassicCopyJob`, and calls `process.AddJob`. A final configuration job sets process parallelism, then `Prepare` resolves jobs and `Run` executes them.

## State and persistence behavior

The executable owns transient `PropertyList` result objects and deletes them after execution. Persistent effects are delegated to copy jobs writing targets, creating directories, ZIP appends, and optional target removal on failure. Environment state in `DefaultEnv` is process-local. The scope-exit PostMaster stop is a shutdown side effect.

## Dependencies and integration points

Dependencies include `XrdApps/XrdCpConfig`, `XrdApps/XrdCpFile`, `CopyProcess`, `DefaultEnv`, `Log`, `FileSystem`, `Utils`, `DlgEnv`, optimizers, `XrdSys` helpers, and private utility obfuscation. It is built as the `xrdcp` executable in `XrdCl/CMakeLists.txt`.

It integrates with `CopyProcess` via property names, with `ClassicCopyJob` and TPC jobs through those properties, with `ProgressDisplay` through result keys such as `sourceCheckSum`, `targetCheckSum`, `additionalCkeckSum`, `size`, and `status`, and with `DefaultEnv` for all runtime tuning.

## Risks and edge cases

`AppendCGI` appends `?` and then may append `&` based only on whether any ampersand exists; URLs with an existing `?` but no `&` get `&` inserted, while edge cases around trailing delimiters are fragile. Recursive path handling relies on `XrdCpFile` directory offsets and manual slash manipulation.

The code pushes result objects even if `AddJob` fails, then continues building jobs. Depending on the failure, later `Prepare`/`Run` may not reflect every reported `AddJob` error. Parallel progress output is protected by a mutex but writes to shared stderr from other code can still interleave.

The result key `additionalCkeckSum` is misspelled consistently with `ClassicCopyJob`. Changing it would break CLI output unless both sides migrate. Remote target pre-stat can fail with errors other than not-found/not-authorized and still leave `targetExists=false`, pushing errors later into open time.

## Test signals

No direct tests are included. High-value tests would invoke `xrdcp` for local copies, force/continue validation, checksum print modes, multiple-source directory requirements, remote target stat errors, recursive remote indexing with a fake filesystem, CLI environment overrides, TPC option translation, ZIP append, and progress checksum printing.
