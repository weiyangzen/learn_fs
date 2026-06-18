# sources/test-tools/crashmonkey/code/utils/communication/SocketUtils.h

Purpose: shared constants and data structures for CrashMonkey control socket communication.

Important APIs/types/functions: `kSocketDir`, `kSocketNameOutbound`, `SocketMessage`, `SocketMessage::CmCommand`, and `SocketError`. Command enum values cover harness error, invalid command, prepare, begin/end log, run tests, checkpoint, and done/failed acknowledgements.

Control flow: no executable flow; consumers use the enum to build protocol messages. State/persistence behavior: fixed socket path `/tmp/crash_monkey_harness` is the integration point between tools and harness.

Dependencies/integration: included throughout `utils/communication` and user tool shims. Risks/test signals: comments warn that socket directory and full path must be kept manually in sync; adding payload-bearing commands requires extending BaseSocket handling.
