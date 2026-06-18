# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/subprocess.cpp

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 178 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `OutputPipeHandler`, `InputPipeHandler`. Important declarations or call sites include `bf::path executable = bp::search_path(command);`; `throw std::runtime_error("Tried to run command " + std::string(command) + " but didn't find it in the PATH");`; `, output_() {`; `output_.reserve(output_.size() + n);`; `output_.insert(output_.end(), vOut_.begin(), vOut_.begin() + n);`; `if (ec) {`; `if (ec != PIPE_CLOSED) {`; `throw SubprocessError(std::string() + "Error getting output from subprocess. Error code: " + std::to_string(ec.value()) + " : "...`; `ba::async_read(pipe_, buffer_, onOutput);`; `ba::async_read(pipe_, buffer_, onOutput);`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `subprocess.h`, `cstdio`, `stdexcept`, `cerrno`, `array`, `boost/process.hpp`, `boost/asio.hpp`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `subprocess.h`, `cstdio`, `stdexcept`, `cerrno`, `array`, `boost/process.hpp`, `boost/asio.hpp`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

## File-Specific Notes
- The subprocess helper uses Boost.Process with Boost.Asio async pipes to avoid stdout/stderr deadlocks while feeding stdin.
