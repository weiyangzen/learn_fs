<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/ipc.c -->
# sources/test-tools/filebench/ipc.c

Purpose: implements Filebench shared-memory IPC, shared object allocation, mutex/condition/rwlock attributes, System V semaphore allocation, and optional ISM-style per-thread memory pools.

Important APIs/functions: `ipc_init()` creates and mmaps a temporary shared-memory file, zeroes pre-pool state, initializes locks/conds/rwlocks, sets defaults, and prepares semaphore keys. `ipc_attach()` maps a worker process at the master-supplied address. `ipc_malloc()`/`ipc_free()` allocate typed objects from fixed pools tracked by bitmaps. `ipc_stralloc()`, `ipc_pathalloc()`, and `ipc_cvar_heapalloc()` allocate from linear shared buffers. `ipc_seminit()`, `ipc_semidalloc()`, and `ipc_semidfree()` manage shared semaphores. `ipc_ismcreate()`, `ipc_ismmalloc()`, and `ipc_ismdelete()` manage a separate shared memory segment.

Control flow: master calls `ipc_init()` before parser and object definitions; worker processes call `ipc_attach()` and then use the already-initialized shared state. Allocators lock `shm_malloc_lock`, scan type-specific bitmaps from the last index, zero the selected object, and return typed pool addresses.

State/persistence: `filebench_shm` points to `filebench_shm_t`, a large shared object containing global lists, locks, counters, fixed pools, bitmaps, string/path heaps, cvar heap, eventgen state, run flags, and plugin selection. Shared-memory files are created under `/tmp` with generated suffixes and unlinked in `ipc_fini()`.

Dependencies/integration: central to fileset/procflow/threadflow/flowop/variable/randdist/cvar allocation. Integrates with `misc.c` logging, parser lifecycle, proc worker exec, flowop synchronization, and platform pthread/process-shared/robust mutex features.

Risks: pool sizes are fixed compile-time limits; exhaustion often aborts. `ipc_stralloc()`/`ipc_pathalloc()` use `strncpy()` for `strlen()` bytes and rely on prezeroed memory for null termination. `ipc_free()` does little bounds validation. `ipc_ismmalloc()` has an explicit no-out-of-memory check comment. Mapping workers at exactly the master's address is fragile under ASLR, hence parser startup disables ASLR.

Test signals: master/worker attach smoke tests, pool exhaustion tests for each object type, robust mutex behavior after owner death, semaphore allocation exhaustion, string/path heap boundaries, and ISM allocation with multiple worker processes.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/ipc.c -->
