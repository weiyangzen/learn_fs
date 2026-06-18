# sources/user-network-fs/samba/source3/script/tests/timelimit.c

Purpose: small utility that runs a command with a maximum wall-clock timeout and signal handling suitable for Samba test harness use.

Important functions and APIs: uses POSIX `fork`, `execvp`, `setpgid`, `wait`, `kill`, `signal`, and `alarm`. `new_process_group()` places the child in a new process group. `sig_alrm_term()` sends SIGTERM to the child process group and schedules SIGKILL after 5 seconds. `sig_term()` handles parent SIGTERM/SIGINT/SIGQUIT similarly with a 1-second kill grace. `sig_usr1()` forwards SIGTERM without exiting immediately.

Control flow: parse `<time> <command>`, fork, exec the command in the child, install signal handlers in the parent, set the timeout alarm, wait until no children remain, then kill the child process group with SIGKILL and exit with the last child exit status.

State and persistence: no persistent state. Runtime state is the global `child_pid`, process group membership, and alarm timers.

Dependencies and integration: imported by `selftest/tests.py` through `selftesthelpers.timelimit` and used as a wrapper for long-running blackbox tests. It assumes process-group signaling is available.

Risks and test signals: `WEXITSTATUS(status)` is used without checking `WIFEXITED`, so signal-terminated children may yield misleading exit codes. The final unconditional SIGKILL is defensive but can report ESRCH silently. Test signal is a nonzero exit with "Maximum time expired" when timeout escalation occurs.
