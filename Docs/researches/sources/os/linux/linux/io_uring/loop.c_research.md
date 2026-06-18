# File Research: sources/os/linux/linux/io_uring/loop.c

Implements a generic io_uring loop runner used when `ctx->loop_step` is installed.

Behavior:
- `io_run_loop()` verifies task-work ownership with `io_allowed_run_tw()`, locks `uring_lock`, and runs `__io_run_loop()`.
- Each iteration calls `ctx->loop_step(ctx, &lp)`, waits for requested CQ progress using `lp.cq_wait_idx`, runs pending task work/local work, handles signals, and flushes CQ overflow.
- `io_loop_wait()` sets `ctx->cq_wait_nr`, sleeps interruptibly if no immediate work/completions/overflow exist, then restores state.

This file is small but important for special in-kernel loop integrations that need repeated io_uring progress without re-entering normal syscall submission.
