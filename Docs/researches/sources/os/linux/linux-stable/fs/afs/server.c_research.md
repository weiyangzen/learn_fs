# File Research: sources/os/linux/linux-stable/fs/afs/server.c

## Scope

Manages AFS fileserver records: lookup by UUID or RxRPC peer, creation, address discovery, probing, reference/active counts, update, expiration, and destruction.

## APIs And Behavior

- `afs_find_server()` maps an incoming RxRPC peer to an active server reference.
- `afs_lookup_server()` finds or creates a UUID-keyed server, looks up addresses through the VL service, probes the server, and waits for concurrent creation if needed.
- `afs_get_server()`, `afs_use_server()`, `afs_put_server()`, `afs_unuse_server()`, and `afs_unuse_server_notime()` manage object and active-use lifetimes.
- Timer/destroyer paths expire inactive servers, give up callbacks, unbind peer appdata, remove proc/probe links, and RCU-free records.
- `afs_check_server_record()` refreshes address lists when a server is marked stale, serializing updates with a flag bit.

## State And Dependencies

Servers live in each cell's UUID rb-tree and the net namespace proc list. Each server owns endpoint state, probe state, callback token data, volume links, timer/work items, locks, and cell references. Address discovery depends on VL cursor operations and AFS/YFS VL address RPCs.

## Risks And Invariants

Creation uses `UNCREATED`/`CREATING` bits plus waiters to avoid duplicate records. Active count zero starts GC unless the server or cell is already expiring. Peer appdata must be cleared before final server destruction to prevent stale callback routing.
