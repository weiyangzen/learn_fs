# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/env.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 50 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `void setenv(const char* key, const char* value) {`; `int retval = ::setenv(key, value, 1);`; `if (0 != retval) {`; `throw std::runtime_error("Error setting environment variable. Errno: " + std::to_string(errno));`; `void unsetenv(const char* key) {`; `int retval = ::unsetenv(key);`; `if (0 != retval) {`; `throw std::runtime_error("Error unsetting environment variable. Errno: " + std::to_string(errno));`; `void setenv(const char* key, const char* value) {`; `int retval = _putenv(command.str().c_str());`. CMake commands used here include `if`, `setenv`. Primary includes/dependencies visible in the file include `env.h`, `stdexcept`, `string`, `cerrno`, `cstdlib`, `Windows.h`, `sstream`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `env.h`, `stdexcept`, `string`, `cerrno`, `cstdlib`, `Windows.h`, `sstream`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.
