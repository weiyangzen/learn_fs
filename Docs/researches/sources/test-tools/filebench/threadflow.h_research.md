# `sources/test-tools/filebench/threadflow.h`

Purpose: Declares Filebench threadflow data structures, async I/O list support, thread attributes, and thread lifecycle APIs.

Important APIs and types: `threadflow_t` contains name, attributes, instance/running/abort flags, unique id, parent procflow pointer, pthread id, mutex, instance AVD, next pointer, per-thread flowop list, private memory, file descriptor and fileset arrays, stats, current flowop start time, optional AIO list, and I/O priority AVD. With `HAVE_AIO`, `aiolist_t` wraps `aiocb64` entries and read/write type. Public functions include `threadflow_define()`, `threadflow_find()`, `threadflow_init()`, `flowop_start()`, `threadflow_allstarted()`, and `threadflow_delete_all()`.

Control flow and integration: Parser-created threadflow masters are cloned by `threadflow_init()` at process start. `flowop_start()` is the execution entry point for worker threads. Procflow startup and shutdown call the exported functions to wait for thread start and delete runtime instances.

State and persistence: Threadflow objects live in Filebench IPC/shared memory and own per-thread runtime state for a workload process. File descriptors and fileset entries are local to each worker thread and are not persisted after run cleanup.

Dependencies: Includes `filebench.h`, `struct flowstats` via included definitions, and forward references procflow/flowop/fileset types.

Risks and test signals: `THREADFLOW_MAXFD` statically caps local file slots. Struct layout changes affect shared-memory users. Tests should compile with and without `HAVE_AIO`, verify thread-local fd rotation behavior, and run multi-thread workloads with private memory and I/O priority attributes.
