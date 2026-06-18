# File Research: sources/os/linux/linux/io_uring/waitid.c

Asynchronous `waitid` support for io_uring. This file arms child-exit waitqueue callbacks, integrates cancellation, copies siginfo to userspace, and completes waitid requests through task_work.

Key responsibilities:
- Prepares waitid requests by allocating async wait state and storing `which`, pid, options, and optional siginfo pointer.
- Uses `kernel_waitid_prepare()` and `__do_wait()` to perform or arm waits.
- Installs a callback on `current->signal->wait_chldexit`.
- Cancels individual or all waitid requests through the cancel framework.
- Copies native or compat siginfo fields to userspace on completion.
- Frees pid references and async data.

Important data flows:
- Issue prepares wait options, sets an initial reference, adds the request to `ctx->waitid_list`, installs the waitqueue entry, then calls `__do_wait()`.
- If `__do_wait()` returns `-ERESTARTSYS`, the request remains armed until child wakeup or cancellation.
- Wake callback validates the child with `pid_child_should_wake()`, removes the wait entry, claims ownership via refs, and queues task_work.
- Task_work retries `__do_wait()`, rearms on another `-ERESTARTSYS`, or completes and copies siginfo.

Concurrency and locking:
- `ctx->uring_lock` protects `waitid_list` and cancellation.
- `iw->refs` combines ownership references with a cancel flag.
- `iw->head` is acquire/release protected so removal can safely find and detach from the waitqueue.
- Waitqueue removal locks the child-exit waitqueue head.

Important invariants:
- Cancel marks the cancel flag even if it cannot claim ownership, preventing later rearm.
- Positive wait result maps to success with `SIGCHLD` in siginfo.
- Async data owns `wo_pid` and must `put_pid()` exactly once.
