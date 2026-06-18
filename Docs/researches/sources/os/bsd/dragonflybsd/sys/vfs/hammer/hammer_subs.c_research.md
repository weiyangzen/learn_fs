# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_subs.c

Purpose: contains HAMMER structural locking, reference-count interlocks, sync-lock wrappers, and miscellaneous conversion/hash helpers shared across the filesystem.

Locking primitives: `hammer_lock_ex_ident()`, `hammer_lock_ex_try()`, `hammer_lock_sh()`, `hammer_lock_sh_try()`, `hammer_lock_upgrade()`, `hammer_lock_downgrade()`, `hammer_unlock()`, and `hammer_lock_status()` implement a compact shared/exclusive lock in `struct hammer_lock`. Exclusive locking is recursive for the owning thread; shared locking while owning exclusive is treated as a debug-critical case but allowed after incrementing the count.

Reference interlocks: `hammer_ref()`/`hammer_rel()` maintain structural references. `hammer_ref_interlock()`, `hammer_ref_interlock_true()`, `hammer_ref_interlock_done()`, `hammer_rel_interlock()`, `hammer_rel_interlock_done()`, `hammer_get_interlock()`, `hammer_try_interlock_norefs()`, and `hammer_put_interlock()` combine ref transitions with a serialized CHECK/LOCKED/WANTED protocol used by buffer, node, volume, and inode lifecycle paths.

Sync lock: `hammer_sync_lock_ex()`, `hammer_sync_lock_sh()`, `hammer_sync_lock_sh_try()`, and `hammer_sync_unlock()` wrap `hmp->sync_lock` and track transaction lock references. The comments define the invariant: metadata mutations under shared sync lock belong to the same flush group, while the flusher uses exclusive sync lock.

Miscellaneous helpers: the file maps HAMMER object types to vnode and directory-entry types, converts between HAMMER time and `timespec`, maps GUIDs/UUIDs, computes `fsid` device values, implements no-history deletion policy, parses snapshot/PFS TID strings, and chooses HAMMER block size/offset across the extended-buffer demarcation.

Directory hashing: `hammer_direntry_namekey()` implements legacy ALG0 and segmented ALG1 hashes. ALG1 hashes filename segments separated by punctuation into upper key bits and adds a full-name CRC component to reduce collisions; the function avoids zero and reserves positive key space for normal directory entries.

Research notes: this file defines low-level invariants assumed by every other file in the group. The custom ref interlock API is subtle: a return value of `1` means the caller owns a transition/check responsibility, not necessarily that the reference count stayed at zero or one.
