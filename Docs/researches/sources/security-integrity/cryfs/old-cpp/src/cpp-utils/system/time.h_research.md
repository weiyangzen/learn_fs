# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/time.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 40 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_SYSTEM_TIME_H`. Important declarations or call sites include `timespec now();`; `inline bool operator<(const timespec &lhs, const timespec &rhs) {`; `inline bool operator>(const timespec &lhs, const timespec &rhs) {`; `return !operator>(lhs, rhs);`; `return !operator<(lhs, rhs);`. Primary includes/dependencies visible in the file include `time.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `time.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.
