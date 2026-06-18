# File Research: sources/os/linux/linux/io_uring/loop.h

Declares loop-mode support.

Key contents:
- `struct iou_loop_params` currently carries `cq_wait_idx`, the CQE index hint to wait for.
- Return values: `IOU_LOOP_CONTINUE` and `IOU_LOOP_STOP`.
- `io_has_loop_ops()` checks `ctx->loop_step` with `data_race()`.
- `io_run_loop()` is the exported runner used by `io_uring_enter()` when loop ops exist.
