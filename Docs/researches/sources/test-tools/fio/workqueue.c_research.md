# sources/test-tools/fio/workqueue.c

Purpose: generic pthread-backed workqueue used by fio to offload submit/work processing to a bounded set of worker threads.

Important APIs/functions: `workqueue_init()` initializes locks/conds, allocates workers, starts threads, and waits until all are running. `workqueue_enqueue()` chooses an idle or least-recent worker, appends work, updates sequence, and signals. `workqueue_flush()` waits until all workers report idle. `workqueue_exit()` signals exit, joins workers, runs callbacks, and frees resources. Internal `worker_thread()` initializes per-worker state, optionally applies nice value, loops over work lists, calls pre-sleep hooks, executes `ops.fn`, and updates accounting.

Control flow/state: workers own `work_list`, flags (`IDLE`, `RUNNING`, `EXIT`, `ACCOUNTED`, `ERROR`), sequence, and callback-private state. The queue tracks `next_free_worker`, `work_seq`, `wake_idle`, and synchronization objects. Flush is caller-serialized with enqueue.

Dependencies/integration: depends on fio smalloc/sfree, pshared mutex/cond helpers, `flist`, `sk_out` assignment, pthreads, and callback vtable from `workqueue_ops`.

Risks/test signals: start failure after `alloc_worker_fn` may leak callback-private resources if mutex init failed before cleanup. Race safety depends on documented caller serialization. Tests should cover enqueue distribution, flush with pre-sleep callbacks, worker init failure, callback error accounting, and exit with pending work.
