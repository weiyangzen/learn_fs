# File Research: sources/os/linux/linux/io_uring/uring_cmd.c

io_uring passthrough command implementation. This file supports driver-defined `uring_cmd` operations, cancellation, async completion, fixed-buffer import, iopoll, multishot polling, and provided-buffer CQE posting.

Key responsibilities:
- Prepares `IORING_OP_URING_CMD` and `IORING_OP_URING_CMD128`.
- Allocates/recycles async command storage, including copied SQEs and vector buffers.
- Calls file `->uring_cmd()` with security checks and io_uring issue flags.
- Lets providers mark commands cancelable and handles cancellation by reinvoking `->uring_cmd()` with cancel flags.
- Provides exported completion helpers for queued commands and CQE32 results.
- Supports fixed-buffer and fixed-vector import for command providers.
- Supports multishot command polling and provided-buffer CQE posting.

Important data flows:
- Prep validates command flags, enforces fixed/multishot constraints, records `cmd_op`, stores the SQE pointer, and allocates async command data.
- Issue builds provider flags for SQE128, CQE32/mixed, compat, and iopoll; calls `file->f_op->uring_cmd()`; then handles queued, retry, multishot, inline complete, or error returns.
- `__io_uring_cmd_done()` removes cancelable tracking, sets result and optional CQE32 extra data, recycles async data, and completes by iopoll marker, deferred completion, or task_work.
- Multishot helpers select provided buffers, post CQEs with `IORING_CQE_F_MORE`, recycle buffers on termination, and arm async poll if requested.

Concurrency and locking:
- Cancelable command list is guarded by `ctx->uring_lock`.
- IOPOLL completion uses release ordering on `req->iopoll_completed`.
- Cleanup avoids cache recycling in unlocked issue contexts.
- IOPOLL commands cannot use cancelable tracking because hash-node storage overlaps with iopoll completion state.

Important invariants:
- Multishot commands must pair with buffer selection and cannot use fixed command mode.
- Providers are responsible for races between normal completion and cancel handling.
- SQE copy size doubles for SQE128 contexts or URING_CMD128 opcodes.
