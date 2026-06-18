# `sources/test-tools/filebench/threadflow.c`

Purpose: Implements Filebench thread-flow lifecycle management inside a procflow. It converts parser-defined master threadflows into runtime worker threads and tears them down during shutdown.

Important APIs and functions: Public functions are `threadflow_define()`, `threadflow_find()`, `threadflow_init()`, `threadflow_allstarted()`, and `threadflow_delete_all()`. Static helpers include `threadflow_define_common()`, `threadflow_createthread()`, `threadflow_kill()`, and `threadflow_delete()`.

Control flow: Parser code creates `FLOW_MASTER` threadflows using `threadflow_define()`. In a child process, `threadflow_init()` locks the shared threadflow list, clones each master according to `tf_instances`, creates pthreads running `flowop_start()`, sets `pf_threads_defined_flag` once all runtime threadflows are defined, then joins created threads. `threadflow_allstarted()` waits for `tf_running` on runtime instances after proc creation. Shutdown calls `threadflow_delete_all()`, which skips masters, marks threads aborted, waits briefly, kills stubborn threads, deletes flowops, destroys locks, and frees threadflow objects.

State and persistence: Threadflows are stored in each procflow’s `pf_threads` list and allocated in Filebench IPC memory. Per-thread state includes unique id, pthread id, abort/running flags, local file descriptors, private memory size, flowop list, stats, and async I/O list when enabled. `shm_required` is incremented/decremented for `THREADFLOW_USEISM`.

Dependencies and integration: Depends on `filebench_shm` locks, IPC allocation, `flowop_start()`, `flowop_delete_all()`, parser-created AVDs, and procflow flags. It is called by `procflow_exec()` and by proc shutdown.

Risks and test signals: `threadflow_delete_all()` advances after freeing the current object in a way that can be risky if list links are invalidated; shutdown tests should stress multiple runtime threads. `pthread_kill(..., SIGKILL)` is process-wide on some systems or invalid for pthread-targeted cleanup assumptions. Shared-memory accounting for private memory must stay balanced. Tests should cover multiple instances, flowop deletion, `THREADFLOW_USEISM`, start-time waits, and thread create failure paths.
