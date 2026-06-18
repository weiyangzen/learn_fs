# sources/object-store/daos/src/engine/srv_internal.h

## Purpose
`srv_internal.h` is the internal contract shared by DAOS engine implementation files. It defines xstream, scheduler, telemetry, NUMA, and chore queue data structures plus prototypes and inline helpers used across startup, scheduling, RPC dispatch, IV, and service lifecycle code.

## Important APIs, Types, and Functions
Core types include `struct dss_xstream`, `struct sched_info`, `struct sched_stats`, `struct sched_hist_seq`, `struct mem_stats`, `struct dss_chore_queue`, `struct engine_metrics`, and `struct dss_numa_info`. It declares globals such as `dss_engine_metrics`, `dss_hostname`, `dss_topo`, `dss_core_nr`, `dss_sys_xs_nr`, `dss_helper_pool`, `dss_tgt_offload_xs_nr`, and scheduler tunables. Inline helpers include `sched_relax_mode2str`, `sched_relax_str2mode`, `sched_xstream_stopping`, `sched_create_task`, `sched_create_thread`, `dss_xs2tgt`, and `dss_xstream_has_nvme`.

## Control Flow
The header does not execute top-level control flow, but its inlines gate common runtime paths. `sched_create_task/thread` reject creation when the current xstream is stopping, update busy timestamps for non-periodic work, and enqueue into the generic Argobots pool. `dss_xs2tgt` maps xstream ids to VOS targets differently depending on helper-pool layout. `dss_xstream_has_nvme` determines where NVMe contexts and poll ULTs are created.

## State and Persistence Behavior
The structures describe live in-memory state: per-xstream scheduler queues/counters, RPC counters, TSE scheduler, shutdown futures, telemetry handles, memory usage counters, chore queues, and topology data. No persistent state is stored here, but fields like target id, context id, start metrics, and rank metrics reflect persistent service identity.

## Dependencies and Integration Points
This header depends on DAOS engine public headers, telemetry, and GURT heap/list types. It links `init.c`, `srv.c`, `sched.c`, `module.c`, `server_iv.c`, metrics, and dRPC-related code. It is not a public API for external modules beyond engine internals.

## Risks
Because it exposes shared structs, layout changes affect many translation units. The inline `sched_xstream_stopping` assumes TLS is initialized for ULT callers and bypasses main-thread callers. `dss_xs2tgt` asserts ids are in range and depends on global target/helper counts being initialized. Adding fields without initialization in `srv.c` can produce subtle scheduler or shutdown bugs.

## Test Signals
Build coverage across all engine files is the main signal. Runtime tests should validate xstream-to-target mapping for helper layouts, NVMe-capable xstream detection, scheduler create rejection after stopping future is set, relax mode parsing, telemetry pointer initialization, and structure counter assertions during shutdown.
