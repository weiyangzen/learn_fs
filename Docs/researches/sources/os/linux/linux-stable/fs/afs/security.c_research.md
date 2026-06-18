# File Research: sources/os/linux/linux-stable/fs/afs/security.c

## Scope

Handles RxRPC key acquisition, anonymous-key fallback, per-vnode permit caching, and VFS permission checks against AFS ACL access masks.

## APIs And Behavior

- `afs_request_key()` and `afs_request_key_rcu()` find a cell key or use/create the cell anonymous key.
- `afs_cache_permit()` records caller access returned by status-fetching RPCs, building sorted key/access permit lists and deduplicating them through a global hash cache.
- `afs_clear_permits()` and `afs_put_permits()` invalidate and free permit lists with RCU.
- `afs_check_permit()` checks cached access or fetches status to populate it.
- `afs_permission()` maps VFS permission masks to AFS directory/file ACL bits and Unix mode bits, supporting RCU pathwalk fallback.
- `afs_clean_up_permit_cache()` warns if permit cache buckets remain populated at module exit.

## State And Dependencies

Uses global `afs_permits_cache`, `afs_permits_lock`, and `afs_key_lock`, plus each vnode's RCU `permit_cache`. It depends on kernel keyrings, `key_type_rxrpc`, status fetching, callback-break validation, and vnode status fields.

## Risks And Invariants

Permit lists are immutable once published and keyed by key pointer/access pairs. Callback breaks or changed access must detach stale permit lists before reuse. RCU permission checks must return `-ECHILD` when key acquisition or validation cannot be completed locklessly.
