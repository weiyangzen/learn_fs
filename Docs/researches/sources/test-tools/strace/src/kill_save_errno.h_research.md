# sources/test-tools/strace/src/kill_save_errno.h

Purpose: provides a tiny helper that sends a signal without clobbering the caller's `errno`.

Important APIs/types/functions: `kill_save_errno(pid_t pid, int sig)`, `kill`, `errno`, `<sys/types.h>`, and `<signal.h>`.

Control flow: saves current `errno`, calls `kill(pid, sig)`, restores saved `errno`, and returns the `kill` result code.

State and persistence behavior: temporarily observes and restores thread-local `errno`; no persistent state.

Dependencies and integration points: used in code paths where strace must signal processes while preserving an earlier syscall/diagnostic error.

Risks: callers must inspect the returned `kill` status because `errno` will not describe `kill` failure afterward. This is intentional but easy to misuse.

Test signals: unit or integration checks should set `errno`, call success and failure cases, assert `errno` is unchanged, and verify the return code is propagated.
