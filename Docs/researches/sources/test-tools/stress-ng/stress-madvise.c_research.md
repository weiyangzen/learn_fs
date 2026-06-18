# sources/test-tools/stress-ng/stress-madvise.c

Purpose: implements `madvise`, a VM/OS stressor for page advice, process advice, proc-map reads, mapping churn, and selected invalid-advice/error paths.

Important APIs/types/functions: `madvise_ctxt_t` carries mapping, size, proc paths, threading, and hardware-poison configuration. `stress_sigbus_handler()` recovers from SIGBUS via `siglongjmp`. `stress_random_advise()` chooses and validates advice while limiting `MADV_HWPOISON`/`MADV_SOFT_OFFLINE`. `stress_madvise_pages()` applies advice across pages and tests invalid cases. `stress_process_madvise()` exercises pidfd-based advice.

Control flow: the stressor maps a guard page, creates and unlinks a temp backing file, fills it, then repeatedly maps file-backed or anonymous memory. It initializes/touches/randomizes pages, calls process-level advice, runs page advice from worker threads when pthreads exist, tests zero-size/invalid-size/invalid-advice calls, optionally checks `MADV_FREE` races, unmaps, tests unmapped/wrapped addresses, cycles advice on `NULL,0`, and increments bogo ops.

State and persistence: temporary backing file state is unlinked and directory removed. Static SIGBUS count and poison counters persist within the process. Metrics are mostly informational counts/logs rather than per-advice rates.

Dependencies/integration: depends on `madvise`, optional pthreads, pidfd/process_madvise shims, core madvise option tables, mincore, mmap, OOM adjustment, and temp-file helpers.

Risks/test signals: hardware poisoning is destructive and is opt-in/capped. Advice can raise SIGBUS or alter page contents. Useful signals are no unrecovered SIGBUS, bounded mmap retries, optional MADV_FREE race log, skip on missing resources, and successful cleanup.
