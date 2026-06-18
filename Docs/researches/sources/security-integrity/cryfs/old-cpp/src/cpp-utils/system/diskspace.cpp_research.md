# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/diskspace.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 40 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `statvfs`. Important declarations or call sites include `uint64_t free_disk_space_in_bytes(const bf::path& location) {`; `int result = ::statvfs(location.string().c_str(), &stat);`; `if (0 != result) {`; `throw std::runtime_error("Error calling statvfs(). Errno: " + std::to_string(errno));`; `uint64_t free_disk_space_in_bytes(const bf::path& location) {`; `if (!GetDiskFreeSpaceEx(location.string().c_str(), &freeBytes, nullptr, nullptr)) {`; `throw std::runtime_error("Error calling GetDiskFreeSpaceEx(). Error code: " + std::to_string(GetLastError()));`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `diskspace.h`, `sys/statvfs.h`, `cerrno`, `Windows.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `diskspace.h`, `sys/statvfs.h`, `cerrno`, `Windows.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.
