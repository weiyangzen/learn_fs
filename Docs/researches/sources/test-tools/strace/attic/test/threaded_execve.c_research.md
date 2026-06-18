<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/threaded_execve.c -->
# sources/test-tools/strace/attic/test/threaded_execve.c

Purpose: complex threaded execve reproducer for strace cases where an execing non-leader thread replaces the thread-group leader.

Important APIs/macros: defines portable `clone2` wrapper variants, raw syscall macros for `tgkill`, `getpid`, `gettid`, and `exit`, globals `my_name` and `leader_final_action`. `thread1` writes `1` and pauses. `thread2` writes `2`, sleeps briefly, tries `execl("/proc/self/exe", ...)`, falls back to resolved `my_name`, then pauses on failure. `thread_leader` creates clone threads with `CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM`, then exits, pauses, or spins based on `leader_final_action`.

Control flow: initial process resolves its executable, sets unbuffered stdout, optionally handles re-exec mode, prints leader pid, arms an alarm, and starts thread orchestration. Re-exec increments the action argument.

State and persistence: process/thread state only; re-execs same binary through `/proc/self/exe` or saved path.

Dependencies and integration: Linux clone/thread semantics, `/proc/self/exe`, raw syscalls, and strace `-f`/`-ff` log routing.

Risks: architecture-specific clone stack handling, intentional infinite loops, malloced stacks never freed, and timing-sensitive behavior. Test signals: strace logs should attribute post-exec output to the leader pid correctly and avoid leaks/confusion across repeated alarm-bounded runs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/threaded_execve.c -->
