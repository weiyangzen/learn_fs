# sources/user-network-fs/samba/source3/torture/test_pthreadpool_tevent.c

Purpose: This file tests integration between Samba's pthread pool wrapper and tevent request polling. It submits one background job and verifies completion through the tevent-facing API.

Important APIs/types/functions: `run_pthreadpool_tevent()` creates a poll-backed tevent context, initializes a `pthreadpool_tevent` with pool size 100, submits `job_fn()` through `pthreadpool_tevent_job_send()`, polls the request, receives it with `pthreadpool_tevent_job_recv()`, and frees the pool/context. `job_fn()` writes `4711` to the provided integer and calls `poll(NULL, 0, 100)` to simulate work.

Control flow: The entrypoint initializes event and pool state, sets `val = -1`, submits the job, blocks with `tevent_req_poll()`, checks the receive return code, prints the final value, and returns true on success.

State/persistence behavior: State is entirely in memory: tevent context, thread pool object, tevent request, and an integer passed by pointer to the worker. There is no persistent file or network state. The worker mutates caller-owned stack state, so completion ordering is essential before reading `val`.

Dependencies and integration points: It depends on `lib/pthreadpool/pthreadpool_tevent.h`, `system/select.h`, POSIX `poll()`, and tevent. It validates that asynchronous thread-pool jobs can be driven from Samba's event loop.

Risks: Thread creation or pool initialization can fail under resource limits. The test does not assert the printed value directly after receive, so a future bug that returns success without running the job would only be visible in output unless additional checking is added.

Test signals: Passing requires successful tevent context creation, pool initialization, job send, event polling, and zero return from `pthreadpool_tevent_job_recv()`. The diagnostic value should print `4711`.
