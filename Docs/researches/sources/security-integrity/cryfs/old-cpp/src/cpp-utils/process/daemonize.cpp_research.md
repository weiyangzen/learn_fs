# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/daemonize.cpp

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 73 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `void daemonize() {`; `pid_t pid = fork();`; `if (pid < 0) {`; `exit(EXIT_FAILURE);`; `if (pid > 0) {`; `exit(EXIT_SUCCESS);`; `umask(0);`; `pid_t sid = setsid();`; `if (sid < 0) {`; `LOG(ERR, "Failed to get SID for daemon process");`. CMake commands used here include `if`, `exit`, `umask`, `LOG`, `close`. Primary includes/dependencies visible in the file include `daemonize.h`, `../logging/logging.h`, `sys/types.h`, `sys/stat.h`, `stdio.h`, `stdlib.h`, `fcntl.h`, `errno.h`, `unistd.h`, `syslog.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `daemonize.h`, `../logging/logging.h`, `sys/types.h`, `sys/stat.h`, `stdio.h`, `stdlib.h`, `fcntl.h`, `errno.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.
