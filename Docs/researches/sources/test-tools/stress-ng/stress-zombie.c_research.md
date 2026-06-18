# sources/test-tools/stress-ng/stress-zombie.c

Purpose: implements the `zombie` stressor, rapidly creating child processes that exit into zombie state, optionally using Linux `clone` namespace flags, then reaping them under a configurable per-worker maximum.

Important APIs/types/functions: `stress_zombie`, `stress_zombie_child`, optional `stress_zombie_clone` and `stress_zombie_clone_cap_sys_admin`, `stress_pid_a_zombie`, `stress_zombie_new`, `stress_zombie_head_remove`, `stress_zombie_free`, `stress_zombie_t`, `stress_zombie_list_t`, `stress_zombie_context_t`, `fork`, optional `clone`, `waitpid`, `setpgid`, `/proc/PID/stat` parsing, `stress_capabilities_check`, `stress_kill_pid`, and options `zombie-max` and `zombie-clone`.

Control flow: option parsing selects zombie maximum and clone mode; clone mode is downgraded when unavailable or when `CAP_SYS_ADMIN` is missing. On Linux clone builds it prepares a temporary context path. After synchronization, the main loop allocates or reuses a zombie list node, creates a child by fork or clone, lets the child mark zombie state and exit, records the pid, sets process group, tracks maximum list length, and increments bogo operations. When the configured zombie limit is reached or process creation fails, the head zombie is optionally verified as zombie state and reaped. Shutdown records the maximum zombies metric, reaps all remaining children, frees active and free-list nodes, and removes the temporary path.

State and persistence behavior: global state is the `zombies` active/free linked lists and `zombie_clone` option flag. Each active node stores pid and optional clone stack. Child process table entries persist as zombies only until the parent reaps them. The optional temporary path is removed during cleanup.

Dependencies and integration points: Linux clone namespace coverage is conditional on `clone` and namespace flags; otherwise fork is used. The stressor integrates with stress-ng process state, capability checks, temp path helpers, kill/wait shims, bogo accounting, metrics, and registers as `CLASS_SCHEDULER | CLASS_OS` with optional verification.

Risks and test signals: high `zombie-max` can hit process limits and force reap/retry behavior. `/proc` verification can be inconclusive, so unknown state is treated conservatively. Clone namespace mode may require `CAP_SYS_ADMIN`; the clone child can intentionally leak a socket to exercise namespace/network cleanup. Verification reports pids that never appear as zombies before reaping.
