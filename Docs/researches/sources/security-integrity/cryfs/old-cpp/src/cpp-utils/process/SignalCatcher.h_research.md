# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalCatcher.h

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 44 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SignalCatcherImpl`, `is`, `SignalCatcher`. Macros/constants: `MESSMER_CPPUTILS_PROCESS_SIGNALCATCHER_H_`. Important declarations or call sites include `SignalCatcher(std::initializer_list<int> signals);`; `~SignalCatcher();`; `bool signal_occurred() const {`; `DISALLOW_COPY_AND_ASSIGN(SignalCatcher);`. CMake commands used here include `SignalCatcher`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `cpp-utils/macros.h`, `atomic`, `csignal`, `memory`, `vector`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cpp-utils/macros.h`, `atomic`, `csignal`, `memory`, `vector`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.
