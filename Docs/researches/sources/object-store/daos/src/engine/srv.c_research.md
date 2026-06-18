# sources/object-store/daos/src/engine/srv.c

## Purpose
`srv.c` implements the DAOS engine service runtime: xstream topology, CPU/NUMA binding, CART context creation, per-xstream TLS, NVMe polling, scheduler integration, dRPC listener startup, shutdown draining, memory telemetry, RPC dispatch into the scheduler, and Argobots diagnostics.

## Important APIs, Types, and Functions
Important exports include `dss_ctx_nr_get`, `dss_xstream_set_affinity`, `dss_xstream_exiting`, `dss_xstream_cnt`, `dss_get_xstream`, `dss_sleep`, `dss_rpc_cntr_get`, `dss_rpc_cntr_enter`, `dss_rpc_cntr_exit`, `dss_srv_init`, `dss_srv_fini`, `dss_srv_set_shutting_down`, `dss_dump_ABT_state`, `dss_get_start_epoch`, `dss_set_start_epoch`, `dss_has_enough_helper`, and `dss_bind_to_xstream_cpuset`. `struct dss_xstream_data` owns global xstream lifecycle state.

## Control Flow
`dss_srv_init` allocates the xstream pointer array, creates synchronization primitives, initializes standalone TLS and local DB, registers BIO bulk ops, starts xstreams, notifies BIO that NVMe started, and starts the dRPC listener. `dss_xstreams_init` reads scheduler/chore environment settings and starts system, main I/O, and offload xstreams. Each `dss_srv_handler` sets affinity, initializes TLS/module info, optionally creates a CART context, registers RPC callbacks, initializes the server-side client scheduler, starts NVMe polling and chore queues, waits at the startup barrier, then progresses CART until shutdown.

## State and Persistence Behavior
Global runtime state includes target/helper counts, system xstream count, helper-pool mode, NVMe health bypass, start epoch, and `xstream_data`. Per xstream state includes scheduler, Argobots pools, shutdown/stopping futures, CART context id, target id, NVMe context, TSE scheduler, chore queue, memory stats, and RPC counters. Persistent storage is touched indirectly through `vos_sys_db_init` and BIO/NVMe contexts.

## Dependencies and Integration Points
The service integrates Argobots, hwloc, CART, dRPC, BIO/NVMe, VOS, telemetry, server TLS, scheduler, module dispatch, RAS/version helpers, and management fail-location parameters. `init.c` calls `dss_srv_init/fini`; CART invokes `dss_rpc_hdlr`; modules provide request attributes and retry-hint encoding.

## Risks
Startup and shutdown have complex synchronization: creator waits for each progress ULT initialization, non-SWIM xstreams wait on a barrier, shutdown sets stopping then shutdown futures, and handlers drain all pools before destroying TLS/CART/NVMe. Incorrect xstream-to-context assertions indicate topology bugs. Affinity selection has edge cases for NUMA, shared helper pools, and reserved system cores. `dss_srv_set_shutting_down` creates tasks on every xstream and assumes prompt execution.

## Test Signals
Coverage should include xstream count/context mapping for helper-pool and per-target helper modes, NUMA and non-NUMA affinity selection, startup failure cleanup at each init step, CART RPC dispatch scheduling and overload retry, NVMe poll ULT startup/failure, graceful shutdown draining blocked ULTs, memory telemetry under `D_MEMORY_TRACK`, dRPC listener lifecycle, and ABT dump signal output.
