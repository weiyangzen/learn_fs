# sources/test-tools/crashmonkey/code/user_tools/end_log.cpp

Purpose: command-line shim that tells the harness to end logging. It closes the logging bracket started by `begin_log`.

Important APIs/types/functions: `ClientCommandSender`, `kSocketNameOutbound`, `SocketMessage::kEndLog`, and expected reply `kEndLogDone`.

Control flow: `main` constructs the sender, connects, sends `kEndLog`, waits for `kEndLogDone`, and returns status. State/persistence behavior: direct filesystem state is unchanged; harness logging state changes.

Dependencies/integration: used by test orchestration and any scripts coordinating log capture. Risks/test signals: socket connection failure, wrong reply, or harness error are reduced to generic negative/nonzero exit codes.
