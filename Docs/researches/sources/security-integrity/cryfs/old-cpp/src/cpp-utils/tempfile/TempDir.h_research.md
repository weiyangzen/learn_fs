# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempDir.h

## Purpose
Implements RAII temporary file and directory helpers for tests and transient filesystem work. This specific file has 26 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `TempDir`. Macros/constants: `MESSMER_CPPUTILS_TEMPFILE_TEMPDIR_H_`. Important declarations or call sites include `TempDir();`; `~TempDir();`; `const boost::filesystem::path &path() const;`; `void remove();`; `DISALLOW_COPY_AND_ASSIGN(TempDir);`. CMake commands used here include `TempDir`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `boost/filesystem.hpp`, `../macros.h`.

## Control Flow
Temporary resources are created at construction or factory time and removed by RAII destruction unless moved away or intentionally released.

## State and Persistence Behavior
State is the filesystem path and ownership flag for the temporary resource; the resource itself exists on disk until RAII cleanup.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `boost/filesystem.hpp`, `../macros.h`.

## Risks and Edge Cases
Temp resource cleanup can fail on open handles or permissions. Path generation must avoid races and predictable names.

## Test Signals
Assert resources exist while owned, disappear after destruction, survive move semantics correctly, and handle nested temp dirs/files.
