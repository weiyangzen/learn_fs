# sources/test-tools/fio/rate-submit.c

Purpose: offloaded IO submission workqueue helpers for fio's rated submission mode.

Important APIs/functions: exported `rate_submit_init()` and `rate_submit_exit()` manage the workqueue when `io_submit_mode == IO_MODE_OFFLOAD`. Workqueue callbacks include `io_workqueue_fn()`, pre-sleep flush/quiesce callbacks, worker allocation/free/init/exit, and accounting update functions. `check_overlap()` serializes overlapping IO when `serialize_overlap` is enabled.

Control flow: initialization creates a workqueue with one worker per requested iodepth. Each worker owns a copied `thread_data` configured from the parent, duplicates files/options, loads and initializes the IO engine, and then submits `io_u` work items. `io_workqueue_fn()` optionally waits until no in-flight overlap exists, marks the IO, queues it, handles busy/completion paths, updates queue events, and signals the parent if errors occur. Exit aggregates worker stats into the parent and frees worker resources. Accounting periodically sums per-direction byte/block counters under locks unless atomic fetch-add is available.

State and persistence: worker-private `thread_data` copies hold IO engine/file state. Parent `td->io_wq` owns worker lifecycle and stat locks. Global `overlap_check` mutex is used by overlap serialization.

Dependencies and integration: fio core thread data, IO engines, workqueue framework, file duplication, option duplication/free, runstate management, rusage, and stats aggregation.

Risks: this path is concurrency-heavy. Deadlock avoidance depends on consistent lock ordering in `pthread_double_lock()`. Worker copies must stay synchronized with parent fields that are safe to duplicate. Overlap checking unlock/relock loops can be expensive under heavy overlapping workloads. Per-priority stats are disabled during exit because aggregation cannot fully preserve them.

Test signals: offload mode with multiple iodepths, serialize-overlap workloads, busy IO engines, error propagation, stat aggregation, workqueue shutdown, and ThreadSanitizer-style race testing where possible.
