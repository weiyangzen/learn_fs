# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalCatcher.cpp

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 134 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SignalCatcherRegistry`, `SignalCatcherRegisterer`, `SignalCatcherImpl`. Important declarations or call sites include `void got_signal(int signal);`; `void add(int signal, details::SignalCatcherImpl* signal_occurred_flag) {`; `_catchers.write([&] (auto& catchers) {`; `catchers.emplace_back(signal, signal_occurred_flag);`; `void remove(details::SignalCatcherImpl* catcher) {`; `_catchers.write([&] (auto& catchers) {`; `auto found = std::find_if(catchers.rbegin(), catchers.rend(), [catcher] (const auto& entry) {return entry.second == catcher;});`; `ASSERT(found != catchers.rend(), "Signal handler not found");`; `catchers.erase(--found.base()); // decrement because it's a reverse iterator`; `~SignalCatcherRegistry() {`. CMake commands used here include `ASSERT`, `SignalCatcherRegistry`, `DISALLOW_COPY_AND_ASSIGN`, `SignalCatcherRegisterer`, `SignalCatcherImpl`, `for`. Primary includes/dependencies visible in the file include `SignalCatcher.h`, `SignalHandler.h`, `algorithm`, `stdexcept`, `vector`, `cpp-utils/assert/assert.h`, `cpp-utils/thread/LeftRight.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `SignalCatcher.h`, `SignalHandler.h`, `algorithm`, `stdexcept`, `vector`, `cpp-utils/assert/assert.h`, `cpp-utils/thread/LeftRight.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.
