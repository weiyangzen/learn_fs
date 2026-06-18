# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/AssertFailed.h

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 26 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `AssertFailed`. Macros/constants: `MESSMER_CPPUTILS_ASSERT_ASSERTFAILED_H`. Important declarations or call sites include `explicit AssertFailed(std::string message) : _message(std::move(message)) { }`; `const char *what() const throw() override {`; `return _message.c_str();`. Primary includes/dependencies visible in the file include `stdexcept`, `string`, `../macros.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `stdexcept`, `string`, `../macros.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.
