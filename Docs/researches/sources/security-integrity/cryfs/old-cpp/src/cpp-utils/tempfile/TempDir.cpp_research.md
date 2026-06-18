# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempDir.cpp

## Purpose
Implements RAII temporary file and directory helpers for tests and transient filesystem work. This specific file has 33 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `: _path(bf::unique_path(bf::temp_directory_path() / "%%%%-%%%%-%%%%-%%%%")) {`; `bf::create_directory(_path);`; `TempDir::~TempDir() {`; `remove();`; `void TempDir::remove() {`; `if (bf::exists(_path)) {`; `bf::remove_all(_path);`; `} catch (const boost::filesystem::filesystem_error &e) {`; `LOG(ERR, "Could not delete tempfile.");`; `const bf::path &TempDir::path() const {`. CMake commands used here include `remove`, `if`, `LOG`. Primary includes/dependencies visible in the file include `TempDir.h`, `../logging/logging.h`.

## Control Flow
Temporary resources are created at construction or factory time and removed by RAII destruction unless moved away or intentionally released.

## State and Persistence Behavior
State is the filesystem path and ownership flag for the temporary resource; the resource itself exists on disk until RAII cleanup.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `TempDir.h`, `../logging/logging.h`.

## Risks and Edge Cases
Temp resource cleanup can fail on open handles or permissions. Path generation must avoid races and predictable names.

## Test Signals
Assert resources exist while owned, disappear after destruction, survive move semantics correctly, and handle nested temp dirs/files.
