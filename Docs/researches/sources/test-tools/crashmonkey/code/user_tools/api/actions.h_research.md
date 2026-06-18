# sources/test-tools/crashmonkey/code/user_tools/api/actions.h

Purpose: public user-tool API header declaring `Checkpoint()`, the small operation workloads call to ask the CrashMonkey harness to mark a checkpoint in the disk log. It is the C++ facade used by generated workloads and the `cm_checkpoint` CLI.

Important APIs/types/functions: namespace `fs_testing::user_tools::api` and function `int Checkpoint()`. The header has only include guards and no dependencies beyond namespace declarations.

Control flow: none in the header; implementation lives in `src/actions.cpp`, where `Checkpoint` sends a socket command and waits for `kCheckpointDone`. State/persistence behavior: calling this API records harness state rather than directly mutating the filesystem.

Dependencies/integration: integrated by `wrapper.cpp`, generated tests, and `cm_checkpoint.cpp`. Risks/test signals: its return contract is integer-only and does not expose detailed socket or harness failure causes.
