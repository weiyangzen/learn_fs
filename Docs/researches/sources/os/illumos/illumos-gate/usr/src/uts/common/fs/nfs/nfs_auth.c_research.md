# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_auth.c

## Purpose

This file implements kernel-side NFS export authorization caching and mountd door callouts. It decides whether a client/security flavor/credential tuple has read-write, read-only, denied, wrong-security, mapped-anonymous, root, group, or limited NFS access to an export.

## Main Responsibilities

- Maintain per-export authorization caches.
- Call userland `mountd` through a door when cache data is missing or refreshed.
- Support per-zone NFS authorization state.
- Start and stop an async refresh thread for stale cache entries.
- Reclaim idle auth-cache entries under memory pressure.
- Provide NFSv4-specific access wrappers:
  - `nfsauth4_access()`
  - `nfsauth4_secinfo_access()`
- Provide common access entry point:
  - `nfsauth_access()`

## Main Data Structures

- `nfsauth_globals_t`
  - Per-zone state for mountd door handle, refresh queue, refresh thread state, and synchronization.
- `refreshq_exi_node_t`
  - Queue node grouping stale auth entries by export.
- `refreshq_auth_node_t`
  - Queue node for one stale auth cache entry and the netid that triggered refresh.
- `auth_cache_clnt`
  - Per-client-address cache node, stored in export hash buckets as AVL trees.
- `auth_cache`
  - Per-client, per-flavor, per-credential authorization entry.

## Lifecycle

Global lifecycle:

- `nfsauth_init()` creates the `exi_cache_handle` kmem cache for `struct auth_cache`.
- `nfsauth_fini()` destroys that kmem cache.

Zone lifecycle:

- `nfsauth_zone_init()` allocates per-zone state, initializes mountd and refresh locks, creates the refresh queue, and stores it in `ng->nfs_auth`.
- `nfsauth_zone_shutdown()` stops the refresh thread if running, drains queued refresh work, frees invalid auth entries, releases export holds, and destroys queued lists.
- `nfsauth_zone_fini()` releases the mountd door handle, destroys locks/CVs/lists, and frees per-zone state.

Mountd door lifecycle:

- `mountd_args()` looks up a door by ID, replaces the per-zone mountd door handle, and releases any previous handle.
- `nfsauth_retrieve()` holds the door handle while calling `door_ki_upcall_limited()` and handles revoked/stale door cases.

## Important Control Flow

`nfsauth_access()`:

1. Initializes uid/gid outputs, mapping root to export anonymous identity by default.
2. Reads the security flavor from `req->rq_xprt->xp_cookie`.
3. Finds matching export security info.
4. Falls back to `AUTH_NONE` when configured.
5. Grants pseudo/export namespace read-only access when a flavor exists only because of NFSv4 namespace setup and is not explicitly exported.
6. Uses fast-path permission checks when no root/none/map lists are involved.
7. Calls `nfsauth_cache_get()` when mountd policy data is needed.
8. Clears supplemental groups for denied or wrong-security results.
9. Retries through `AUTH_NONE` on wrong security where allowed.
10. Normalizes denied results to `NFSAUTH_DENIED`.

`nfsauth4_access()`:

- Calls `nfsauth_access()`.
- If denied or wrong-security, allows `NFSAUTH_LIMITED` when `has_visible(exi, vp)` reports visible subexports below the vnode.

`nfsauth4_secinfo_access()`:

- Checks whether a security flavor is explicitly exported with `M_4SEC_EXPORTED`.
- Uses fast RO/RW decisions when no lists are involved.
- Otherwise calls `nfsauth_cache_get()`.

`nfsauth_cache_get()`:

1. Copies and masks the client address using transport address mask.
2. Hashes the masked address into `exi->exi_cache`.
3. Finds or creates an `auth_cache_clnt` AVL node for the client.
4. Finds or creates an `auth_cache` node keyed by flavor and credential identity.
5. Waits if another thread is already retrieving the entry.
6. For new entries, calls `nfsauth_retrieve()` synchronously and publishes the result.
7. For fresh entries, returns cached uid/gid/groups/access and updates use time.
8. If the entry is older than `NFSAUTH_CACHE_REFRESH`, marks it stale and queues async refresh work.
9. If allocation fails, falls back to uncached `nfsauth_retrieve()`.

`nfsauth_retrieve()`:

- Builds a versioned `varg_t` request for `NFSAUTH_ACCESS`.
- XDR-encodes the request with `xdr_varg()`.
- Calls mountd over a kernel door.
- Retries when the door is not established, returns `NFSAUTH_DROP` after repeated absence, and handles revoked/stale handles.
- XDR-decodes `nfsauth_res_t`.
- Copies returned server uid/gid/groups to caller-owned storage.

`nfsauth_refresh_thread()`:

- Waits for queued stale cache entries.
- Marks entries `NFS_AUTH_REFRESHING`.
- Calls `nfsauth_retrieve()` without blocking foreground access paths.
- Updates cached access and mapped identity on success.
- Returns entries to `NFS_AUTH_FRESH` and wakes waiters.
- Frees entries that were invalidated while refresh was in flight.

Reclaim path:

- `exi_cache_reclaim()` walks all NFS server zones.
- `exi_cache_reclaim_zone()` walks exports in each zone.
- `exi_cache_trim()` removes auth entries idle longer than `NFSAUTH_CACHE_TRIM`, avoiding entries in `NFS_AUTH_WAITING`, marking stale/refreshing entries invalid, and freeing empty client nodes.

## Synchronization

- `mountd_lock` protects the per-zone mountd door handle.
- `refreshq_lock` and `refreshq_cv` protect the async refresh queue and refresh thread state.
- `exi->exi_cache_lock` protects per-export auth-cache bucket trees.
- `auth_cache_clnt::authc_lock` protects each client’s credential/flavor AVL tree.
- `auth_cache::auth_lock` and `auth_cv` protect individual auth entry state transitions.

## Cache Timing

- `NFSAUTH_CACHE_REFRESH`: 600 seconds before an entry is considered stale and scheduled for refresh.
- `NFSAUTH_CACHE_TRIM`: 3600 idle seconds before memory-pressure reclaim may trim an entry.

## Dependencies

- Door APIs:
  - `door_ki_lookup`
  - `door_ki_hold`
  - `door_ki_rele`
  - `door_ki_upcall_limited`
  - `door_ki_info`
- XDR routines:
  - `xdr_varg`
  - `xdr_nfsauth_res`
- Export/security structures from `<nfs/export.h>` and `<nfs/auth.h>`.
- AVL trees and kernel synchronization primitives.
- NFS zone globals:
  - `nfs_srv_getzg`
  - `nfssrv_globals_list`
  - `nfssrv_globals_rwl`

## State and Memory Ownership

- Cached server supplemental groups are owned by `auth_cache` entries and freed in `nfsauth_free_node()`.
- Returned supplemental groups from `nfsauth_cache_get()` are caller-owned copies.
- Client address buffers in `auth_cache_clnt` are heap-owned and freed in `nfsauth_free_clnt_node()`.
- The copied request address in `nfsauth_cache_get()` is freed on all normal paths.
- Refresh queue nodes hold export references with `exi_hold()` and release them with `exi_rele()`.

## Risks and Edge Cases

- Door absence returns `NFSAUTH_DROP` after retries so clients retransmit rather than receiving a hard denial.
- The refresh thread intentionally lets stale data serve foreground requests while refreshing asynchronously.
- Cache comparator includes flavor, uid, gid, group count, and group data. The group `memcmp()` length is the group count, not `group_count * sizeof (gid_t)`; this should be checked carefully because it may compare only part of the supplemental group array.
- `refreshq_dead_entries` exists in `nfsauth_globals_t` but is not used in this file.
- Reclaim uses try-locking to avoid blocking under memory pressure, so reclaim may fail partially and increments failure counters.
- Invalidated stale/refreshing entries are removed from trees but freed later by refresh/queue handling.

## Testing Notes

Useful coverage should include:

- Fast-path RO/RW access with no lists.
- AUTH_NONE fallback and `NFSAUTH_MAPNONE`.
- Wrong-security retry behavior.
- Root anonymous mapping.
- New cache entry retrieval, cache hit, stale async refresh, and trim reclaim.
- Mountd door missing, revoked, stale, and decode-failure cases.
- Concurrent lookup where one thread waits on `NFS_AUTH_WAITING`.
- Zone shutdown while refresh entries are queued or refreshing.
