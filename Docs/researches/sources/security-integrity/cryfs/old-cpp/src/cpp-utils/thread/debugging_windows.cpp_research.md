# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging_windows.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 112 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `NameData`, `ModuleHandle`, `Fn`, `APIFunction`. Important declarations or call sites include `~NameData() {`; `if (nullptr != LocalFree(name)) {`; `throw std::runtime_error("Error releasing thread description memory. Error code: " + std::to_string(GetLastError()));`; `ModuleHandle(const char* dll) {`; `bool success = GetModuleHandleExA(0, dll, &module);`; `if (!success) {`; `throw std::runtime_error(string() + "Error loading dll: " + dll + ". Error code: " + std::to_string(GetLastError()));`; `~ModuleHandle() {`; `bool success = FreeLibrary(module);`; `if (!success) {`. CMake commands used here include `if`, `ModuleHandle`, `APIFunction`, `ASSERT`. Primary includes/dependencies visible in the file include `Windows.h`, `debugging.h`, `codecvt`, `cpp-utils/assert/assert.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Windows.h`, `debugging.h`, `codecvt`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.
