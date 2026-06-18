# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/dir_cache.rs

Purpose: manages per-open-directory handles and cached directory entries for low-level readdir.

Important APIs: `OpenDirHandle(FileHandle)` implements `HandleTrait`; `DirCache::new/add/remove/get`; `DirCacheEntry::new`, `dir_ino`, and `get_or_query_entries`.

Control flow and state: `DirCache` wraps a mutex-protected `HandleMap<OpenDirHandle, AsyncDropArc<DirCacheEntry>>`. `add` creates an entry for an inode and returns a handle. `get` clones the async-drop arc. `DirCacheEntry` stores `Option<Vec<DirEntry>>` behind a Tokio mutex; first query fills the cache and all later calls reuse it.

Dependencies and integration: low-level `opendir`, `readdir`, and `releasedir` use it to ensure repeated offset reads see a consistent directory snapshot.

Risks and tests: cache lives until `releasedir`, so changes after open are intentionally hidden. `remove` panics through `HandleMap` if the handle is invalid. Readdir offset behavior has TODO tests.
