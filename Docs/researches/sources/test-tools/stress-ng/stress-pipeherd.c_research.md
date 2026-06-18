# sources/test-tools/stress-ng/stress-pipeherd.c

Purpose: `stress-pipeherd.c` implements the `pipeherd` stressor, simulating a token-passing herd of processes over one pipe to stress pipe wakeups, context switching, and exclusive wait behavior.

Important APIs/types/functions: `stress_pipeherd_data_t` carries a token counter and random check value. `stress_pipeherd_read_write()` repeatedly reads the token, increments the counter, writes it back, and optionally yields. `stress_pipeherd()` owns pipe setup, process herd creation, token recovery, metrics, and verification.

Control flow: the stressor resolves process count and yield option, creates one pipe, optionally enables pipe packet mode with `O_DIRECT` on the write end, writes an initial token, initializes pid tracking, synchronizes, and forks up to `pipeherd-procs` children. Each child runs the token read/write loop until stop. The parent also participates in token passing, then reads the final token, sets bogo ops from the counter, kills/waits children, closes fds, and optionally reports context-switch metrics from `getrusage`.

State and persistence behavior: state is the pipe token, child pid array, optional rusage snapshots, and bogo counter. There are no filesystem artifacts.

Dependencies and integration points: pipe/fcntl packet mode, fork/kill-many helpers, scheduler and parent-death helpers, optional `getrusage` context-switch fields, stress-ng settings, and `CLASS_PIPE_IO | CLASS_MEMORY | CLASS_OS | CLASS_IPC` registration with `VERIFY_ALWAYS`.

Risks: the single pipe is both input and output for all processes, so fairness and wakeup behavior dominate throughput. Fork failures are recorded as pid `-1` without immediate abort. Verification only checks that the token's check field survives; it does not validate every counter transition.

Test signals: `--pipeherd` should produce bogo count equal to the passed token counter and no check mismatch. Variants include min/max `--pipeherd-procs`, `--pipeherd-yield`, packet mode availability, and context-switch metric availability.
