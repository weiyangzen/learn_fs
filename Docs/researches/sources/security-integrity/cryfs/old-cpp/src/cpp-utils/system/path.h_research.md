# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/path.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 27 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_SYSTEM_PATH_H`. Important declarations or call sites include `inline bool path_is_just_drive_letter(const boost::filesystem::path& path) {`; `return path.has_root_path() && !path.has_root_directory() && !path.has_parent_path();`; `inline constexpr bool path_is_just_drive_letter(const boost::filesystem::path& /*path*/) {`. Primary includes/dependencies visible in the file include `boost/filesystem/path.hpp`, `cpp-utils/macros.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `boost/filesystem/path.hpp`, `cpp-utils/macros.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.
