# sources/object-store/rustfs/crates/ecstore/src/store/peer.rs

## Purpose
This file handles local disk discovery, local disk ID caching, lock-client initialization, local peer naming, disk information collection, and capacity checks used by `ECStore` startup and placement decisions. It is the local-node hardware/topology utility layer for store initialization and admin/storage introspection.

## Important APIs, Types, And Functions
- `find_local_disk` looks up a `DiskStore` by endpoint/path in `GLOBAL_LOCAL_DISK_MAP`.
- `find_local_disk_by_ref` resolves either an endpoint/path or disk UUID, using and prewarming `GLOBAL_LOCAL_DISK_ID_MAP`.
- `get_disk_via_endpoint` maps an `Endpoint` to a disk through `GLOBAL_LOCAL_DISK_SET_DRIVES` when populated, falling back to endpoint string lookup.
- `all_local_disk_path`, `all_local_disk`, and `prewarm_local_disk_id_map` enumerate local disks and cache UUID-to-path mappings.
- `init_local_disks(endpoint_pools)` constructs `DiskStore`s for local endpoints and fills global path and pool/set/disk-index maps.
- `init_lock_clients(endpoint_pools)` creates local or remote namespace-lock clients per unique host:port and publishes global lock client maps.
- `init_local_peer(endpoint_pools, host, port)` sets `GLOBAL_LOCAL_NODE_NAME`.
- `get_disk_infos` gathers `DiskInfo` from available disks.
- `has_space_for` enforces usable-capacity and inode guards for an erasure set.

## Control Flow
Local disk lookup first tries direct endpoint/path strings. UUID lookup parses the reference, checks the cached UUID map, and if necessary scans all local disks calling `get_disk_id` until a match is found. `init_local_disks` preallocates the global pool/set/disk matrix based on endpoint topology, creates disks only for local endpoints, stores them by endpoint string, and also places them into the indexed matrix.

`init_lock_clients` deduplicates endpoints by host:port, creates `LocalClient` for local endpoints and `RemoteClient` for remote URLs, publishes the first local client as the global lock client, then publishes the full map. `init_local_peer` prefers the host portion of local URL endpoints and falls back to configured host/port or `127.0.0.1`.

`has_space_for` doubles known object sizes, requires more than half the disks to have info, rejects low-inode disks outside single-drive erasure mode, checks per-disk free space, and ensures remaining aggregate free space stays above the configured fill fraction.

## State And Persistence Behavior
The module mutates process-global runtime maps rather than durable storage:
- `GLOBAL_LOCAL_DISK_MAP` maps endpoint string to local disk handle.
- `GLOBAL_LOCAL_DISK_ID_MAP` maps disk UUID to endpoint/path.
- `GLOBAL_LOCAL_DISK_SET_DRIVES` maps pool/set/disk indices to local disk handles.
- Global lock clients are published through `set_global_lock_client` and `set_global_lock_clients`.
- `GLOBAL_LOCAL_NODE_NAME` is set for peer identity.
No on-disk metadata is written here except whatever `new_disk` or disk info calls perform internally.

## Dependencies And Integration Points
This file depends on endpoint topology, `DiskStore`, `DiskOption`, `new_disk`, global store maps, lock client types (`LocalClient`, `RemoteClient`, `LockClient`), disk info APIs, erasure mode flags, disk capacity constants, UUID parsing, tracing, and `ECStore` placement logic. `init.rs` and `rebalance.rs` rely on these helpers for startup and pool capacity selection.

## Risks And Edge Cases
- Global vectors are appended in `init_local_disks`; repeated calls without clearing could duplicate topology entries.
- `init_lock_clients` deduplicates by host:port, so different endpoints sharing a host:port but different paths collapse to one lock client, which is likely intended for node-level locks but should remain explicit.
- `find_local_disk_by_ref` may perform a full local disk scan and disk ID I/O when the cache is cold.
- `all_local_disk` unwraps values after filtering `is_some`; safe in current code but brittle under refactor.
- `init_local_peer` unwraps URL host after checking `has_host`.
- `has_space_for` uses `disk.total - disk.used` and assumes disk info invariants prevent underflow.

## Test Signals
No tests are defined in this file. Related tests in `init.rs` cover local peer/pool ownership indirectly. High-value direct tests would cover UUID cache lookup/fallback, indexed disk lookup with and without `GLOBAL_LOCAL_DISK_SET_DRIVES`, lock-client deduplication, repeated `init_local_disks` behavior, and `has_space_for` edge cases for half-online disks, inode exhaustion, unknown sizes, and fill fraction limits.
