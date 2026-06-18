# sources/test-tools/crashmonkey/code/user_tools/src/actions.cpp

Purpose: implements the checkpoint user API by sending a command to the CrashMonkey harness over the local control socket. It is the bridge between workload code and harness-side checkpoint handling.

Important APIs/types/functions: `Checkpoint()`, `ClientCommandSender`, `kSocketNameOutbound`, `SocketMessage::kCheckpoint`, and `kCheckpointDone`. It lives in `fs_testing::user_tools::api`.

Control flow: `Checkpoint` constructs `ClientCommandSender` with the outbound socket and command pair, then returns `Run()`. `Run` performs connect, send, receive, and response-type validation.

State/persistence behavior: no direct file writes; success indicates the harness acknowledged a checkpoint marker, which later affects epoch/crash-state generation. Dependencies/integration: used by wrapper `DefaultFsFns::CmCheckpoint`, generated workloads, and `cm_checkpoint.cpp`.

Risks/test signals: assumes one fixed socket path and a responsive harness. Return codes preserve only coarse failure stages, so callers generally treat any nonzero as workload failure.
