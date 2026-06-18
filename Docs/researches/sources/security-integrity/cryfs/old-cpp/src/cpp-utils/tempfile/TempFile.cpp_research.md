# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempFile.cpp

## Purpose
Implements RAII temporary file and directory helpers for tests and transient filesystem work. This specific file has 48 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `: _path(path) {`; `if (create) {`; `ofstream file(_path.string().c_str());`; `if (!file.good()) {`; `throw std::runtime_error("Could not create tempfile");`; `: TempFile(bf::unique_path(bf::temp_directory_path() / "%%%%-%%%%-%%%%-%%%%"), create) {`; `TempFile::~TempFile() {`; `if (exists()) {`; `remove();`; `} catch (const boost::filesystem::filesystem_error &e) {`. CMake commands used here include `if`, `remove`, `LOG`. Primary includes/dependencies visible in the file include `TempFile.h`, `../logging/logging.h`, `fstream`.

## Control Flow
Temporary resources are created at construction or factory time and removed by RAII destruction unless moved away or intentionally released.

## State and Persistence Behavior
State is the filesystem path and ownership flag for the temporary resource; the resource itself exists on disk until RAII cleanup.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `TempFile.h`, `../logging/logging.h`, `fstream`.

## Risks and Edge Cases
Temp resource cleanup can fail on open handles or permissions. Path generation must avoid races and predictable names.

## Test Signals
Assert resources exist while owned, disappear after destruction, survive move semantics correctly, and handle nested temp dirs/files.
