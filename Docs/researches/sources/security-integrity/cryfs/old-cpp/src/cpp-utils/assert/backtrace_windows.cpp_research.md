# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace_windows.cpp

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 187 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SymInitializeRAII`. Macros/constants: `HANDLE_CODE`. Important declarations or call sites include `std::string exception_code_string(DWORD exception_code) {`; `switch (exception_code) {`; `return str.str();`; `, success(::SymInitialize(process, NULL, TRUE)) {`; `~SymInitializeRAII() {`; `::SymCleanup(process);`; `std::string backtrace_to_string(CONTEXT* context_record) {`; `if (!sym.success) {`; `DWORD error = GetLastError();`; `memset(&stack_frame, 0, sizeof(stack_frame));`. CMake commands used here include `switch`, `HANDLE_CODE`, `SymInitializeRAII`, `if`, `memset`, `while`, `GetCurrentThread`, `SymSetOptions`, `LOG`, `return`, `RtlCaptureContext`. Primary includes/dependencies visible in the file include `backtrace.h`, `string`, `sstream`, `../logging/logging.h`, `Dbghelp.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `backtrace.h`, `string`, `sstream`, `../logging/logging.h`, `Dbghelp.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.
