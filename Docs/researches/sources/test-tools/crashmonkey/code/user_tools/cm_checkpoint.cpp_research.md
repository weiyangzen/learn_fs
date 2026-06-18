# sources/test-tools/crashmonkey/code/user_tools/cm_checkpoint.cpp

Purpose: command-line checkpoint trigger for the CrashMonkey harness. It exposes the `Checkpoint()` API as an executable.

Important APIs/types/functions: `fs_testing::user_tools::api::Checkpoint` and `main`. There are no arguments or local helpers.

Control flow: `main` directly returns `Checkpoint()`, which sends the harness checkpoint socket command and waits for `kCheckpointDone`. State/persistence behavior: inserts a logical checkpoint marker into the harness/log stream rather than writing user data.

Dependencies/integration: useful for shell-driven workloads and for wrapper `DefaultFsFns::CmCheckpoint`. Risks/test signals: the executable has no usage checks and no diagnostic output on failure.
