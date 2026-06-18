# File Research: sources/os/linux/linux/io_uring/tw.h

Header for io_uring task_work helpers.

Key responsibilities:
- Defines default local task_work batch size.
- Provides `io_should_terminate_tw()` termination predicate for exiting tasks, fallback kernel workers, or dying rings.
- Declares normal/local/fallback task_work add/run helpers.
- Provides inline dispatch from `__io_req_task_work_add()` to local or normal task_work.
- Provides inline pending checks and permission checks for deferred taskrun.

Important invariants:
- `io_tw_lock()` asserts `ctx->uring_lock` is already held.
- Deferred taskrun work is allowed only for the ring submitter task.
- `io_run_task_work()` clears notification signals and handles PF_IO_WORKER-specific resume/task_work paths.
