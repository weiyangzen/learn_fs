# sources/storage-engines/foundationdb/flow/Platform.cpp research

## Purpose

`Platform.cpp` is Flow's cross-platform OS abstraction and diagnostics implementation. It covers CPU, memory, disk, network, timer, random, file, path, directory, thread, allocation, temporary-file, crash, backtrace, dynamic-library, executable-path, and run-loop profiling services. It is shared infrastructure under the networking/runtime layer and hides platform differences among Linux, FreeBSD, macOS, and Windows.

## Important APIs, types, and functions

Resource-stat APIs include `getProcessorTimeThread`, `getProcessorTimeProcess`, `getResidentMemoryUsage`, `getMemoryUsage`, `getMachineRAMInfo`, `getDiskBytes`, `getNetworkTraffic`, `getMachineLoad`, `getDiskStatistics`, `getDeviceId`, and `getSystemStatistics`. Linux-specific helpers parse `/proc/self/statm`, `/proc/meminfo`, `/proc/zoneinfo`, `/proc/net/dev`, `/proc/net/snmp`, `/proc/stat`, and `/proc/diskstats`; Windows uses PDH counters; macOS uses Mach, sysctl, and IOKit.

Time APIs are `timer_monotonic`, `timer`, `timer_int`, `getLocalTime`, and `epochsToGMTString`, backed by platform-specific `OffsetTimer` implementations. Memory and allocation APIs include `setMemoryQuota`, `allocate`, `allocateInternal`, `mmapSafe`, `mprotectSafe`, large-page enablement, `platform::outOfMemory`, and allocation instrumentation initialization.

Filesystem/path APIs include `joinPath`, `renameFile`, `atomicReplace`, `deleteFile`, `platform::createDirectory`, `cleanPath`, `popPath`, `abspath`, `parentDirectory`, `basename`, `getUserHomeDirectory`, `findFiles`, `platform::listFiles`, `platform::listDirectories`, `platform::findFilesRecursively`, `platform::findFilesRecursivelyAsync`, `fileExists`, `directoryExists`, `fileSize`, `fileModifiedTime`, `readFileBytes`, `writeFileBytes`, and `writeFile`. `platform::TmpFile` manages a temporary file lifecycle.

Process/thread APIs include `threadSleep`, `threadYield`, `platform::setCloseOnExec`, `startThread`, `waitThread`, `setThreadPriority`, `platform::getEnvironmentVar`, `platform::setEnvironmentVar`, `platform::getWorkingDirectory`, `platform::getDefaultConfigPath`, `platform::getDefaultClusterFilePath`, `criticalError`, `flushAndExit`, `platformInit`, crash-handler registration, backtrace formatting, dynamic library load/unload/symbol lookup, `exePath`, `getExecPath`, `setupRunLoopProfiler`, and `stopRunLoopProfiler`.

## Control flow

`getSystemStatistics` is stateful across calls. It lazily allocates `SystemStatisticsState`, samples wall time and CPU clocks, computes deltas when initialized, records memory and disk capacity, then uses platform-specific counters to compute machine network, disk, and CPU deltas. On Unix, current counters are read from kernel interfaces and compared with the previous state. On Windows, PDH counters are initialized once and queried thereafter.

File replacement flow in `atomicReplace` creates a random temp file in the target directory, preserves ownership and mode on Unix when replacing an existing file, writes text or binary content, flushes, fsyncs/FlushFileBuffers outside simulation, closes, and renames/replaces atomically. Directory creation recursively creates missing path components. Path resolution uses `realpath` for existing prefixes and `cleanPath` for non-existing suffixes when `mustExist` is false.

Thread creation on Unix wraps user functions in `runFunc` so uncaught `std::exception`s print a backtrace and exit instead of silently killing the thread. Run-loop profiling on Linux installs a `SIGPROF` handler for the profiled network thread and starts a monitor thread that watches `net2RunLoopIterations` and `net2RunLoopSleeps`; it sends signals when the loop appears blocked or saturated, and `Net2::run` later harvests sampled backtraces.

Crash handling on Linux registers signal handlers for fatal signals, optionally `SIGTERM` under coverage builds, prints/traces the signal and stack, runs registered callbacks, flushes traces, restores the default action, and re-sends the signal. `criticalError` and `flushAndExit` provide explicit fatal exits with trace/stdout flushing and optional abort for core dumps.

## State and persistence behavior

Most state is process-local: static timers, PDH query handles, last sampled system-stat counters, large-page fallback flags, allocation-instrumentation buffers, crash-handler callbacks, profiling thread state, profiling counters, and temporary file names. Persistent side effects include file creation/replacement/deletion, directory tree deletion, temporary files, environment variable mutation, thread creation, memory quotas, and dynamic library loads. `atomicReplace` is the most persistence-sensitive function because it promises durable replacement outside simulation and preserves file metadata on Unix.

## Dependencies and integration points

The file depends on the platform C APIs (`pthread`, `mmap`, `getrusage`, `statvfs`, `getifaddrs`, `/proc`, `sysctl`, Mach, IOKit, Windows PDH/Win32), Boost filesystem/format/asio, Abseil stacktrace on non-Apple Unix, `fmt`, and many Flow helpers: `TraceEvent`, `Error`, `FaultInjection`, `Knobs`, `ScopeExit`, `SimpleCounter`, `StreamCipher`, `UnitTest`, and `Util`. `Net2.cpp` integrates with this file for timers, disk capacity, close-on-exec, thread start/wait, yielding, profiling toggles, and shared Linux profiling globals.

## Risks and edge cases

This file has high portability risk. Different platforms return different statistics and units, and some paths are explicitly less tested, such as FreeBSD disk stats. Kernel pseudo-file parsing can break if formats change or if containers expose partial cgroup/proc data. Several functions intentionally throw `platform_error` or `io_error` after tracing, so callers must be ready for system-level failures.

Filesystem correctness is subtle: `abspath(resolveLinks=false)` is asserted incomplete, `atomicReplace` must avoid leaving temp files or losing permissions, `createDirectory` handles races and historical kernel bugs, and recursive deletion uses `nftw`/`remove`. The crash and profiling signal handlers knowingly use operations that are not fully async-signal-safe because they run during fatal or diagnostic paths. `allocate` aborts through `platform::outOfMemory` when mmap/VirtualAlloc fails; guard pages change the returned pointer relative to the mapped region and must match deallocation expectations elsewhere.

## Test signals

Inline tests cover Linux memory-info parsing and extensive path/directory operations, including symlink resolution on Unix. Additional useful signals are platform-specific noSim tests for `atomicReplace` durability and permissions, temp-file lifecycle, directory recursion, environment access, random byte generation, thread wrapper exception behavior, memory quota failure paths, disk/network stat deltas, crash-handler smoke tests under controlled signals, dynamic library load/symbol lookup, and run-loop profiler enable/disable behavior.
