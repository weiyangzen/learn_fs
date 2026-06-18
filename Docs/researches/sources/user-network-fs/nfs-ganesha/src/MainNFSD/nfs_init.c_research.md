<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_init.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_init.c

## Purpose
Owns daemon initialization and lifecycle state: global parameters, prereqs, config reload, package setup, NFSv4 identity, service threads, capability lowering, malloc trim scheduling, health checks, and `nfs_start()`.

## Important APIs, Types, And Functions
- Globals include `nfs_param`, `nfs_health_`, `nfs_init`, boot time/epoch, verifiers, node identity, thread IDs, config/pid paths, and NFSv4 owner/scope.
- `nfs_prereq_init()`, `nfs_set_param_from_conf()`, `init_server_pkgs()`, `nfs_Init()`, `nfs_Start_threads()`, `nfs_start()`, `reread_config()`, and `nfs_health()` are the central lifecycle functions.

## Control Flow
After config parsing, callers invoke `nfs_start()`. It stores start info, sets umask and write verifiers, optionally lowers caps, initializes caches/RPC/admin/callback/Kerberos via `nfs_Init()`, starts service threads, schedules malloc trim, marks init complete, registers with FSAL backends, initializes stats, and waits for the admin thread. `sigmgr_thread()` handles SIGHUP reload and SIGTERM shutdown.

## State And Persistence Behavior
Mutates process-global runtime state and indirectly creates persistent recovery/grace/export/RPC registrations. Health snapshots are retained in `healthstats`.

## Dependencies And Integration Points
Integrates config parsing, logging, nTIRPC, FSAL/MDCACHE, SAL state, NFS protocols, DBus, QOS, idmapper, uid2grp, netgroup, pNFS, recovery, callbacks, monitoring, 9P, NLM/NSM, RADOS URLs, fridgethr, and Linux capabilities.

## Risks
- Startup order is tightly coupled.
- Config reload supports only selected dynamic changes.
- 9P/RDMA dispatcher is noted as never cancelled or cleaned up.
- Health checks are coarse.
- Capability and `PR_SET_IO_FLUSHER` behavior is platform/permission sensitive.

## Test Signals
Test startup matrices across optional features, reload transitions, SIGHUP/SIGTERM, stalled queue health, partial startup failures, and shutdown after active traffic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_init.c -->
