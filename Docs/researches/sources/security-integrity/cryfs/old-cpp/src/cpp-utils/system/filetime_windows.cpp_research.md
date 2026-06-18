# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime_windows.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 114 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `OpenFileRAII`. Important declarations or call sites include `FILETIME to_filetime(timespec value) {`; `timespec to_timespec(FILETIME value) {`; `if (ticks >= TICKS_TO_UNIX_EPOCH) { // otherwise out of range`; `:handle(CreateFileA(filepath, access, 0, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr)) {`; `BOOL close() {`; `if (INVALID_HANDLE_VALUE == handle) {`; `BOOL success = CloseHandle(handle);`; `~OpenFileRAII() {`; `close();`; `int set_filetime(const char *filepath, timespec lastAccessTime, timespec lastModificationTime) {`. CMake commands used here include `if`, `OpenFileRAII`, `close`. Primary includes/dependencies visible in the file include `filetime.h`, `Windows.h`, `stdexcept`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `filetime.h`, `Windows.h`, `stdexcept`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.
