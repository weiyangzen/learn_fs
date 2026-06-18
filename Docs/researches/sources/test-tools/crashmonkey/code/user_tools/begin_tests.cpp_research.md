# sources/test-tools/crashmonkey/code/user_tools/begin_tests.cpp

Purpose: command-line shim that asks the harness to run loaded tests. It wraps one socket command and expected acknowledgement.

Important APIs/types/functions: `ClientCommandSender`, `kSocketNameOutbound`, `SocketMessage::kRunTests`, and `kRunTestsDone`. There is only `main`.

Control flow: connects to the harness socket, sends `kRunTests`, waits for `kRunTestsDone`, and exits according to command-sender status. State/persistence behavior: no direct persistence; it advances harness control flow into test execution.

Dependencies/integration: used by CrashMonkey orchestration around compiled workloads. Risks/test signals: if the harness returns an error command or wrong command, the process only reports nonzero status.
