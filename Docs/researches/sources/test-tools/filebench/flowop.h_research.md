<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/flowop.h -->
# sources/test-tools/filebench/flowop.h

Purpose: declares the central `flowop_t` execution object, flowop prototype descriptors, type/attribute constants, statistics globals, and lifecycle APIs used by parser, proc/thread execution, and flowop libraries.

Important APIs/types: `flowop_t` holds identity, global/execution/composite links, local variables, thread backpointer, callback function pointers, type/attrs, fileset/fd attributes, AVD runtime attributes, target linkage, stats, synchronization primitives, private buffers, semaphore state, and throughput limiter fields. `flowop_proto_t` maps built-in names to init/execute/destruct callbacks. Constants distinguish prototype (`FLOW_DEFINITION`), inner composite prototype (`FLOW_INNER_DEF`), master script instance (`FLOW_MASTER`), and runtime instances.

Control flow contract: parser code creates `FLOW_MASTER` objects from prototypes and sets AVD attributes. Worker startup clones them into runtime instances. `fo_func`, `fo_init`, and `fo_destruct` are invoked by `flowop.c`; helper APIs expose define/find/init/delete/print and I/O setup to `flowop_library.c`.

State/persistence: instances are shared-memory objects from `ipc_malloc(FILEBENCH_FLOWOP)`. Attributes are mostly `avd_t` so values can be constants, variables, random distributions, or composite locals. Buffers and `fo_private` are process-local allocations owned by callbacks and destructors.

Dependencies/integration: includes `filebench.h`, which supplies `threadflow_t`, `fileset_t`, `avd_t`, `flowstats`, `fb_fdesc_t`, and timing types. Declares local filesystem plugin initialization hooks.

Risks: the struct is copied wholesale for inheritance, so any new pointer or synchronization field needs explicit reset/reinitialization in `flowop_define_common()`. Attribute bitmasks are used for stats classification and file flags; inconsistent callback metadata can corrupt accounting.

Test signals: ABI/build checks should compile every flowop callback table entry; runtime tests should ensure cloned flowops have independent locks, buffers, target lists, and stats.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/flowop.h -->
