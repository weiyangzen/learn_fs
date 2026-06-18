# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/homedir.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 111 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `passwd`, `PathBuffer`. Important declarations or call sites include `bf::path _get_home_directory() {`; `const char* homedir_ = getenv("HOME");`; `if (homedir == "") {`; `struct passwd* pwd = getpwuid(getuid());`; `if (pwd) {`; `if (homedir == "") {`; `throw std::runtime_error("Couldn't determine home directory for user");`; `bf::path _get_appdata_directory() {`; `const char* xdg_data_dir = std::getenv("XDG_DATA_HOME");`; `if (xdg_data_dir != nullptr) {`. CMake commands used here include `if`, `CoTaskMemFree`. Primary includes/dependencies visible in the file include `homedir.h`, `sys/types.h`, `pwd.h`, `Shlobj.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `homedir.h`, `sys/types.h`, `pwd.h`, `Shlobj.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.
