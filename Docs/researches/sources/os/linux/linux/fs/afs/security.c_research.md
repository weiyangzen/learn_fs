# File Research: sources/os/linux/linux/fs/afs/security.c

## Scope

This file handles AFS authentication key selection, anonymous fallback, per-vnode permit caching, and VFS permission checks against AFS ACL-derived access masks.

## Public And Internal APIs Covered

- Key lookup: `afs_request_key()` and RCU-safe `afs_request_key_rcu()`.
- Permit cache lifecycle: `afs_put_permits()`, `afs_clear_permits()`, and module-exit `afs_clean_up_permit_cache()`.
- Permit update/check: `afs_cache_permit()`, `afs_check_permit()`, and internal RCU permit lookup.
- VFS permission hook: `afs_permission()`.

## Control Flow And Behavior

- Key requests use `request_key_net()` for the cell key description. `-ENOKEY` falls back to a lazily allocated anonymous RxRPC null key.
- Permit lists cache caller access returned by file-server status replies for specific keys. Lists are sorted by key pointer, hashed globally, reference-counted, and shared when identical.
- `afs_cache_permit()` updates a vnode permit cache only if the callback break observed during the RPC is still current; otherwise it discards the candidate to avoid caching stale ACL state.
- RCU pathwalk permission checks only use already available validity and permit state; missing data returns `-ECHILD`.
- Blocking permission checks validate the vnode, fetch status if needed, then interpret AFS directory/file permissions.
- Directories require lookup for read/execute/chdir and delete or insert for writes. Files require lookup, mode-bit checks, read ACL for read/exec, and write ACL for writes.

## State And Data Structures

- Global `afs_permits_cache` stores interned `struct afs_permits` lists protected by `afs_permits_lock`.
- `afs_key_lock` serializes anonymous-key allocation per cell.
- Each vnode has an RCU `permit_cache` pointer that is cleared on callback break.

## Dependencies

- Linux keyring RxRPC key type, VFS permission API, RCU, spinlocks, and file-server status fetching.
- AFS callback validity helpers and access-mask constants.

## Risks And Invariants

- Permit caches are valid only while callback state remains unbroken.
- RCU readers must not observe freed permit/key memory; permit destruction is deferred through `call_rcu()`.
- Anonymous-key checks are special-cased to use `vnode->status.anon_access`.
