# `sources/test-tools/filebench/procflow.h`

Purpose: Declares the Filebench process-flow object and the public process lifecycle API used by parser, runtime, and child-process entry code.

Important APIs and types: `procflow_t` stores process name, instance number, configured instance AVD, running flag, `pf_threads_defined_flag`, list linkage, PID, thread id, owned threadflow list, attributes, and nice value AVD. Public functions are `procflow_define()`, `proc_create()`, `procflow_shutdown()`, `proc_shutdown()`, and `procflow_exec()`.

Control flow and integration: Parser code creates `FLOW_MASTER` procflows with `procflow_define()`. Runtime code calls `proc_create()` to clone masters and start child processes. Child filebench instances call `procflow_exec()` using command-line process name and instance. Shutdown code uses `procflow_shutdown()` or `proc_shutdown()` to stop workers and clean shared memory.

State and persistence: The struct is allocated from Filebench IPC/shared-memory allocation classes and linked under `filebench_shm->shm_procflowlist`, allowing parent and child processes to coordinate via shared flags and lists.

Dependencies: Includes `filebench.h` for `avd_t`, `flag_t`, `pid_t`, `pthread_t`, constants such as `FLOW_MASTER`, and shared-memory definitions. It forward-references `struct threadflow` to avoid direct header coupling.

Risks and test signals: Any change to `procflow_t` affects shared memory ABI inside Filebench worker processes. Tests should cover parser-created process definitions, multi-instance cloning, child process lookup, and shutdown synchronization across process boundaries.
