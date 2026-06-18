<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_admin_thread.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_admin_thread.c

## Purpose
Implements the admin thread, DBus admin interface, shutdown trigger, and orderly shutdown sequence for Ganesha.

## Important APIs, Types, And Functions
- `nfs_Init_admin_thread()` initializes admin synchronization and DBus paths.
- `admin_halt()` sets `admin_shutdown` and wakes the admin thread.
- `admin_thread()` waits for shutdown and invokes `do_shutdown()`.
- DBus methods cover grace, shutdown, DRC info, cache purges, fd limit init, malloc trace/trim, config reload, and version properties.

## Control Flow
Startup initializes mutex/condition state and optional DBus registration. The admin thread blocks until `admin_halt()`. Shutdown stops URL watchers, DBus, delayed executor, QOS, state async requests, RPC, monitoring, reaper, 9P workers, general fridge, pNFS DSs, exports, recovery, callback RPC, and FSALs, using emergency FSAL cleanup if thread shutdown is disorderly.

## State And Persistence Behavior
State includes `admin_shutdown`, DBus registration, runtime cache contents, malloc trim flag, and pidfile removal. `trim_status` writes `malloc_info()` to `/tmp/mallinfo-<host>.<pid>.txt`.

## Dependencies And Integration Points
Coordinates DBus, config URL/RADOS, delayed executor, QOS, state async, RPC, monitoring, reaper, 9P, general fridge, pNFS, exports, recovery, callbacks, FSALs, idmapper, uid2grp, netgroup, and DRC.

## Risks
- Shutdown order is delicate with active requests.
- DBus malloc tracing accepts an admin-supplied path.
- Config reload is intentionally partial.
- Destroying admin mutex/condvar makes late shutdown signals unsafe.

## Test Signals
Test DBus validation, grace parsing, cache purges, config reload success/failure, shutdown under load, QOS/monitoring shutdown, and Linux/non-Linux malloc controls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_admin_thread.c -->
