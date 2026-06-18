# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/assert.h

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 76 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `DisableAbortOnFailedAssertionRAII`. Macros/constants: `MESSMER_CPPUTILS_ASSERT_ASSERT_H`, `ASSERT`. Important declarations or call sites include `* This implements an ASSERT(expr, msg) macro.`; `: thread_id_(std::this_thread::get_id()) {`; `~DisableAbortOnFailedAssertionRAII() {`; `if (thread_id_ != std::this_thread::get_id()) {`; `LOG(ERR, "DisableAbortOnFailedAssertionRAII instance must be destructed in the same thread that created it");`; `static int num_instances() {`; `inline std::string format(const char *expr, const std::string &message, const char *file, int line) {`; `std::string result = std::string()+"Assertion ["+expr+"] failed in "+file+":"+std::to_string(line)+": "+message+"\n\n" + backtr...`; `auto msg = format(expr, message, file, line);`; `LOG(ERR, msg);`. CMake commands used here include `if`, `LOG`, `abort`. Primary includes/dependencies visible in the file include `AssertFailed.h`, `iostream`, `thread`, `backtrace.h`, `../logging/logging.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `AssertFailed.h`, `iostream`, `thread`, `backtrace.h`, `../logging/logging.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.
