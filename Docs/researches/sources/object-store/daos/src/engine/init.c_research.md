# sources/object-store/daos/src/engine/init.c

## Purpose
`init.c` is the DAOS engine process entry point and lifecycle coordinator. It parses command-line options, initializes global libraries and server subsystems, opens the service to external traffic once management setup completes, handles process signals, and tears the engine down in dependency order.

## Important APIs, Types, and Functions
Public-facing helpers include `dss_set_join_version`, `dss_get_join_version`, `engine_in_check`, `dss_self_rank`, and `get_module_info`. Major private routines are `server_init`, `server_fini`, `dss_topo_init`, `abt_init`, `modules_load`, `dss_crt_event_cb`, `dss_crt_hlc_error_cb`, `server_id_cb`, `parse`, and `main`. Global configuration includes `daos_sysname`, `dss_hostname`, storage/NVMe/socket paths, NVMe memory sizing, instance index, topology handles, NUMA/core selection, module facility flags, storage tier count, and check mode.

## Control Flow
`main` parses options, blocks normal shutdown/debug signals while leaving fault signals unblocked, registers signal-stack fault handling, calls `server_init`, then waits on `sigwait`. `server_init` sets umask, starts HLC recovery, initializes TLS/debugging/topology/telemetry/dRPC/dbtree/Argobots/module framework/CART/placement/IV/modules/NVMe/services, notifies the parent `daos_server` over dRPC, waits for `DSS_INIT_STATE_SET_UP`, registers CART event/HLC callbacks, opens the xstream barrier, and records readiness metrics. `server_fini` reverses this order while preserving the important rule that module cleanup runs before xstreams are stopped because cleanup may create ULTs.

## State and Persistence Behavior
Most state is process-global configuration. `dss_join_version` is copied into xstream TLS after service startup; `dss_check_mode` changes module selection and retry behavior; topology data caches hwloc state and optional NUMA core maps. HLC recovery deliberately delays startup if needed so post-restart HLC values do not appear older than pre-restart values. Persistent storage is initialized indirectly through VOS/NVMe/server DB paths.

## Dependencies and Integration Points
The file coordinates Argobots, CART, dRPC, telemetry, DAOS debug/logging, TLS, hwloc, placement, handle hash tables, IV, BIO/NVMe, VOS dbtree class registration, and dynamically loaded DAOS modules. It also interacts with management through `drpc_notify_ready`, `ds_notify_*` RAS helpers, and CART rank/dead-rank events.

## Risks
Initialization ordering is fragile: TLS must precede debug ID callbacks, HLC recovery must end before modules read HLC, modules must load before module init, and xstreams must remain alive for cleanup. Topology validation has many edge cases around oversubscription, NUMA split, helper XS count, and `dss_core_offset` being stored as an unsigned sentinel initialized to `-1`. Event handling can intentionally SIGKILL the process when self-exclusion is detected.

## Test Signals
Strong coverage comes from engine startup/shutdown tests with different target/helper/NUMA options, check mode, invalid numeric options, dRPC notify failures, module load failures, CART event callbacks, HLC drift notification, and SIGUSR1/SIGUSR2 Argobots dump paths. Fault-injection around each `server_init` exit label should verify cleanup order and leak-free partial initialization.
