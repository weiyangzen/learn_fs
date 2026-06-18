# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalHandler.h

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 141 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SignalHandlerRAII`, `sigaction`, `on`, `SignalHandlerRunningRAII`. Macros/constants: `MESSMER_CPPUTILS_PROCESS_SIGNALHANDLER_H_`. Important declarations or call sites include `using SignalHandlerFunction = void(int);`; `: _old_handler(), _signal(signal) {`; `std::memset(&new_signal_handler, 0, sizeof(new_signal_handler));`; `int error = sigfillset(&new_signal_handler.sa_mask);  // block all signals while signal handler is running`; `if (0 != error) {`; `throw std::runtime_error("Error calling sigfillset. Errno: " + std::to_string(errno));`; `_sigaction(_signal, &new_signal_handler, &_old_handler);`; `~SignalHandlerRAII() {`; `_sigaction(_signal, &_old_handler, &removed_handler);`; `if (handler != removed_handler.sa_handler) {  // NOLINT(cppcoreguidelines-pro-type-union-access)`. CMake commands used here include `if`, `_sigaction`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `memory`, `csignal`, `cpp-utils/assert/assert.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory`, `csignal`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.
