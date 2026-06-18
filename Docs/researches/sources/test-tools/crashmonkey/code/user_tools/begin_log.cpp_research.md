# sources/test-tools/crashmonkey/code/user_tools/begin_log.cpp

Purpose: command-line shim that tells the CrashMonkey harness to begin logging. It is a small executable front-end around the socket command sender.

Important APIs/types/functions: `ClientCommandSender`, `kSocketNameOutbound`, `SocketMessage::kBeginLog`, and expected reply `kBeginLogDone`. `main` ignores CLI arguments.

Control flow: constructs a command sender for `/tmp/crash_monkey_harness`, sends `kBeginLog`, waits for `kBeginLogDone`, and returns the sender's status. State/persistence behavior: no filesystem mutation directly; it changes harness logging state.

Dependencies/integration: used by scripts or harness phases that need to bracket logging. Risks/test signals: failure detail is collapsed into numeric exit codes from `ClientCommandSender::Run`.
