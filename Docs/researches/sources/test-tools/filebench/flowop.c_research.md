<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/flowop.c -->
# sources/test-tools/filebench/flowop.c

Purpose: implements Filebench flowop lifecycle and scheduling. It defines prototype, master, runtime, and composite flowops; creates runtime instances for worker threads; repeatedly executes each thread's `fo_exec_next` chain; records latency/bytes/count statistics; and destroys flowop-local resources at thread exit.

Important APIs/functions: `flowop_init()` registers generic and filesystem-specific flowops and initializes plugin vectors; `flowop_start()` is the worker thread main loop; `flowop_define()` and `flowop_new_composite_define()` allocate shared-memory flowops; `flowop_find*()` resolves global and recursive flowop names; `flowop_beginop()`/`flowop_endop()` update timing, byte, read/write, global `controlstats`, and optional latency histogram state. Generic init/destruct helpers are used by `flowop_library.c` prototypes.

Control flow: master initialization loads prototype flowops. Parser-created `FLOW_MASTER` flowops are copied into runtime instances inside `flowop_start()` while holding `shm_flowop_lock` and a read side of `shm_flowop_find_lock`; find operations take the write side as a barrier so target lookups wait until runtime creation finishes. The main loop checks thread/global abort flags, quiet mode, and process readiness, then executes the current flowop `fo_iters` times and advances cyclically. Composite flowops recurse through inner flowops and propagate `FILEBENCH_OK`, `FILEBENCH_ERROR`, `FILEBENCH_NORSC`, or `FILEBENCH_DONE`.

State/persistence: all flowop objects are allocated from IPC shared memory and linked both globally (`fo_next`) and per execution list (`fo_exec_next`/`fo_comp_fops`). Per-flowop mutexes, condition variables, private buffers, semaphores, constants, timestamps, target lists, and stats live in `flowop_t`. Runtime thread memory may come from normal heap or ISM.

Dependencies/integration: depends on `filebench_shm`, IPC locks/allocators, parser-created threadflow/procflow structures, fileset lookup, stats data, eventgen counters, ioprio, and flowop library callbacks. `fb_lfs_newflowops()` and `fb_lfs_funcvecinit()` attach local filesystem behavior.

Risks: runtime instance creation inherits whole `flowop_t` objects and must carefully reinitialize locks and list pointers. `flowop_composite_destruct()` advances after deleting the current inner flowop, which is sensitive to use-after-free if deletion mutates links unexpectedly. Stats updates protect global counters but per-flowop stats are updated by owning execution without broad locking. Error paths often call `filebench_shutdown(1)`, so malformed workloads can terminate the whole run.

Test signals: run WML scripts with simple read/write loops, composite flowops, target wakeups, and no-resource modes; confirm flowop lists, instance numbers, abort behavior, latency histograms, and stats totals. Concurrency tests should cover multiple process/thread instances and target lookup ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/flowop.c -->
