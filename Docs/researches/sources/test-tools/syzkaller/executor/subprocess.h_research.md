# sources/test-tools/syzkaller/executor/subprocess.h

Purpose: POSIX subprocess wrapper used by the runner to launch executor children and binary test payloads with controlled fd mappings.

Important APIs and control flow: the constructor builds `posix_spawn_file_actions`, validates source fds do not overlap target fd range, adds requested dup/close actions, closes all other fds up to `kFdLimit`, creates a new process group, and starts the child with ASAN and glibc rseq environment overrides. `KillAndWait` sends `SIGKILL` to the child pid and waits. `WaitAndKill` polls with timeout, kills the process group and pid on timeout, then returns normalized status. `ExitStatus` maps exits, signals, and unusual wait states away from ambiguous `kFailStatus`/0 values.

State and dependencies: owns `pid_`; destructor kills any still-running child. Depends on `posix_spawn`, `waitpid`, `kill`, and executor timing helpers.

Integration points: `executor_runner.h` uses it for persistent `exec` subprocesses and temporary binary execution requests.

Risks and tests: fd remapping is intentionally single-pass and rejects overlapping source fds. `KillAndWait` kills only the top process, while `WaitAndKill` can kill the process group; runner comments acknowledge descendant processes can survive in some hang paths. Test signal is runner integration and timeout behavior.
