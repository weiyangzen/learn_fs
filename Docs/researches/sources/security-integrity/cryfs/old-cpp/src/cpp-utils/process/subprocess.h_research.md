# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/subprocess.h

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 39 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SubprocessResult`, `SubprocessError`, `Subprocess`. Macros/constants: `MESSMER_CPPUTILS_PROCESS_SUBPROCESS_H`. Important declarations or call sites include `SubprocessError(std::string msg) : std::runtime_error(std::move(msg)) {}`; `static SubprocessResult call(const char *command, const std::vector<std::string> &args, const std::string& input);`; `static SubprocessResult call(const boost::filesystem::path &executable, const std::vector<std::string> &args, const std::string...`; `static SubprocessResult check_call(const char *command, const std::vector<std::string> &args, const std::string& input);`; `static SubprocessResult check_call(const boost::filesystem::path &executable, const std::vector<std::string> &args, const std::...`; `DISALLOW_COPY_AND_ASSIGN(Subprocess);`. CMake commands used here include `SubprocessError`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `string`, `vector`, `stdexcept`, `boost/filesystem/path.hpp`, `../macros.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `string`, `vector`, `stdexcept`, `boost/filesystem/path.hpp`, `../macros.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.
