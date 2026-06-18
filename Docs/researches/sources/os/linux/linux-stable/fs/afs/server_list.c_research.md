# File Research: sources/os/linux/linux-stable/fs/afs/server_list.c

## Scope

Builds and maintains per-volume fileserver lists derived from VLDB records.

## APIs And Behavior

- `afs_alloc_server_list()` chooses VLDB sites matching the volume type, applies `DONTUSE` and `NEWREPSITE` replication cutover rules, creates/uses server records, sorts entries by UUID, and returns a refcounted list.
- `afs_annotate_server_list()` detects meaningful changes between old and new lists, including excluded flags and RO replication state.
- `afs_attach_volume_to_servers()`, `afs_reattach_volume_to_servers()`, and `afs_detach_volume_from_servers()` maintain each server's sorted volume attachment list.
- `afs_put_serverlist()` drops server active-use refs and RCU-frees the list.

## State And Dependencies

The list contains `struct afs_server_entry` records with server refs, volume backpointers, flags, callback expiry, and list links. It depends on VLDB parsed entries, `afs_lookup_server()`, cell `vs_lock`, and volume server-list RCU replacement.

## Risks And Invariants

Server lists are sorted by UUID so replacement can preserve callback metadata and reattach efficiently. RO release handling intentionally excludes old or new replica sites until a majority cutover condition is met.
