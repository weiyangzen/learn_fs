# sources/sync-backup/kopia/internal/parallelwork/parallel_work_queue.go

Purpose: implements a dynamically growable parallel work queue where tasks may enqueue more work while workers are running.

Important APIs/types/functions: `Queue`, `CallbackFunc`, `EnqueueFront`, `EnqueueBack`, `Process`, `dequeue`, `completed`, `ProgressCallback`, `OnNthCompletion`, and `NewQueue`.

Control flow: enqueue pushes callbacks to a `container/list` and signals a condition variable. `Process` starts a fixed worker pool under `errgroup`; workers dequeue until the queue is empty and no worker is active. Completion increments counters and wakes waiters. Progress callbacks are rate-limited through `maybeReportProgress`.

State and persistence behavior: in-memory queue, counters, active worker count, and next progress report time protected by `sync.Cond` lock.

Dependencies and integration points: supports upload, validation, and other bulk concurrent workflows.

Risks and test signals: correctness depends on condition signaling and active-worker accounting. Tests cover front/back order, errors, waiting for active workers, progress callbacks, and `OnNthCompletion`.
