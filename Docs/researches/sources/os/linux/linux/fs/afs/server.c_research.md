# File Research: sources/os/linux/linux/fs/afs/server.c

## Scope

This file manages AFS fileserver records: lookup by UUID or RxRPC peer, creation from VLDB data, address-list updates, active/reference counts, garbage collection, callback give-up, and purge waiting.

## Public And Internal APIs Covered

- Lookup/use: `afs_find_server()`, `afs_lookup_server()`, `afs_get_server()`, `afs_use_server()`.
- Release: `afs_put_server()`, `afs_unuse_server()`, `afs_unuse_server_notime()`.
- Maintenance: `afs_purge_servers()`, `afs_wait_for_servers()`, `afs_check_server_record()`.
- Internal helpers allocate/install servers, look up addresses through VL servers, update address records, and run timer/workqueue destruction.

## Control Flow And Behavior

- Servers are stored in a per-cell RB tree keyed by UUID and exposed through a per-net proc list.
- Creating a new server allocates a record marked `UNCREATED`, installs it under the cell write lock, looks up addresses through VLDB, and immediately probes the fileserver.
- Concurrent creators wait on `AFS_SERVER_FL_CREATING`; failure records `create_error` before restoring `UNCREATED`.
- Active counts and references are separate: active use suppresses expiry timers, while references control RCU freeing.
- Unused servers are timer-delayed before GC unless expired or the cell is being removed.
- Destruction removes the server from cell/proc/probe lists, optionally gives up callbacks, unbinds RxRPC peer appdata, drops endpoint state and cell refs, and frees through RCU.
- `afs_check_server_record()` serializes address-list refresh with `AFS_SERVER_FL_UPDATING` and retries waiters a limited number of times.

## State And Data Structures

- `struct afs_server` contains UUID tree node, endpoint state, address version, flags, active/ref counts, timer, destroy work, volumes list, probe state, callback-token data, and service ID.
- Address lookup uses `afs_vl_cursor` and dispatches YFS `GetEndpoints` for YFS VL servers or AFS `GetAddrsU` otherwise.

## Dependencies

- Volume-location client/rotation code, fileserver probing, RxRPC peer appdata, per-cell locks, RCU, timers, and workqueues.

## Risks And Invariants

- Creation failure ordering uses barriers so waiters see `create_error` after `UNCREATED`.
- Server removal must happen only after active use drains.
- Callback give-up is needed before discarding servers that may still hold callback promises.
