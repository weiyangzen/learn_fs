<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/ipc.h -->
# sources/test-tools/filebench/ipc.h

Purpose: defines the shared-memory schema and IPC constants used across Filebench. It is the contract for all global state, object pools, run modes, abort reasons, mutex attributes, and IPC helper APIs.

Important APIs/types: `filebench_shm_t` contains global fileset/procflow/flowop lists and locks, parallel allocation controls, process/run abort state, parser variables, random/custom variable lists, logging/dump settings, eventgen queue, System V semaphore ids, run/misc modes, shared string/path/cvar heaps, ISM allocation pointers, filesystem plugin type, pool bitmaps, last allocation indices, and fixed arrays for every allocatable object. Public functions expose initialization, attach/fini, allocation/free, mutex/cond attributes, semids, strings/paths/cvar heap, mutex wrappers, sem init, and ISM operations.

Control flow contract: master creates and initializes `filebench_shm`; worker processes attach to it. Object modules use `ipc_malloc(type)` and `ipc_free(type, addr)` rather than heap allocation for shared objects. The marker field divides zeroed metadata from nonzeroed large pools during `ipc_init()`.

State/persistence: the header fixes capacities such as filesets, entries, procflows, threadflows, flowops, variables, AVDs, randdists, cvars, string memory, path memory, and cvar heap size. Runtime state persists only for the benchmark process lifetime in mmap/shared memory.

Dependencies/integration: includes `filebench.h` and references most core structs. `shm_filesys_type` connects to `fsplug.h`; run/abort flags are interpreted by parser/procflow/flowop loops.

Risks: changing pool sizes affects shared memory footprint and ABI. The bitmap dimensions use `FILEBENCH_MAXBITMAP`, driven by file entries, for every type, which is simple but large. Typo-prone integer constants are shared across modules and must remain synchronized with allocation switch statements.

Test signals: compile checks for allocation switch coverage when adding a new object type, shared-memory size sanity, and full workload tests that allocate near configured maxima.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/ipc.h -->
