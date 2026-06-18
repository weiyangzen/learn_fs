# sources/test-tools/fio/engines/exec.c

Purpose: Implements a diskless/no-IO `exec` engine that launches an external program during a fio job and terminates it when the fio runtime expires.

Important APIs/functions: Options are `program`, `arguments`, `grace_time`, and `std_redirect`. Internal helpers include `str_replace()`, `expand_variables()`, `exec_background()`, queue/init/cleanup/open callbacks, and the registered `exec` engine.

Control flow: Init requires a program, sets a 50 ms thinktime loop, and forces one pseudo file. On first queue call, `exec_background()` expands `%r` to runtime seconds and `%n` to job name, optionally opens `<job>.stdout` and `<job>.stderr`, forks, redirects child stdio, splits `program arguments` on spaces into an argv array, and calls `execvp()`. Subsequent queue calls sleep for thinktime, check elapsed job runtime, send SIGTERM after timeout, then sleep the grace interval. Cleanup sends SIGKILL if a child pid remains.

State/persistence: Per-thread options store the child pid. Redirect files are created in the current working directory and persist after completion.

Dependencies/integration: Uses fork/execvp, signals, fio time/runstate/thinktime, and fio logging.

Risks: Argument parsing is whitespace-only with no quote or escape handling. Child failure paths may return from the child into fio code rather than `_exit()`. Parent does not wait/reap the child, so zombies are possible until process exit. Timeout handling may send repeated SIGTERM. `str_replace()` can return the original pointer on allocation failure, and `expand_variables()` then frees it as if allocated, creating a potential invalid free.

Test signals: Tests should cover variable expansion, no-argument commands, quoted argument limitations, redirect file creation, timeout/grace termination, cleanup kill, and child exec failure.
