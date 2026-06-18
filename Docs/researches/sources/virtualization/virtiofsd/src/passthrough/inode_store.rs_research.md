# File Research: sources/virtualization/virtiofsd/src/passthrough/inode_store.rs

This file owns passthrough inode identity, lookup deduplication, FUSE refcounting, and safe lifetime handling for migration metadata.

Core data model:
- `Inode = u64`: FUSE inode ID.
- `InodeIds`: host inode tuple: `st_ino`, `st_dev`, and mount ID.
- `InodeData`: FUSE inode ID, `FileOrHandle`, atomic refcount, host IDs, mode, and optional migration info.
- `InodeStoreInner`: maps by FUSE ID, by host IDs, and by file handle.
- `InodeStore`: `Arc<RwLock<InodeStoreInner>>` public wrapper.
- `StrongInodeReference`: counted strong reference that increments/decrements `InodeData.refcount`.

Inode file access:
- `InodeData::get_file()` returns an `InodeFile::Ref` for stored `GuestFile`, opens an `OpenableFileHandle`, or reports invalid migration state.
- `open_file()` reopens stored `O_PATH` FDs through `/proc/self/fd` or opens by handle with requested flags.
- Non-regular and non-directory inodes are protected from unsafe non-`O_PATH` opens via `is_safe_inode()`.
- `get_path()` reads `/proc/self/fd` and rejects non-root nodes reported as `/`, treating them as outside the shared root.
- `identify()` prefers path diagnostics and falls back to inode metadata.

Store behavior:
- `insert_new()` populates all identity maps and asserts FUSE ID uniqueness.
- `remove()` removes all identity entries and drops migration-info strong refs with `drop_unlocked()`.
- `clear_migration_info()` preserves root migration info but clears all other inode migration data safely.
- `claim_inode()` prefers file-handle identity, then falls back to host IDs only for entries backed by a live FD. This avoids inode-number reuse when only a file handle is stored.
- `get_or_insert()` deduplicates existing inodes or inserts a new one with refcount 1.
- `new_inode()` inserts without deduplication, used for known FUSE IDs such as root or deserialized state.

Strong reference behavior:
- `StrongInodeReference::new()` and `new_with_data()` increment the refcount only if it is nonzero.
- `new_no_increment()` is unsafe and requires the caller to have already accounted for the refcount.
- `leak()` transfers the refcount to the guest, which must later send `FORGET`.
- `Drop` decrements refcount and removes the inode when it reaches zero.
- `drop_unlocked()` is the safe path when the inode store is already mutably locked.

Interactions:
- Used by nearly every operation in `passthrough/mod.rs`.
- Migration info may contain `StrongInodeReference`, creating cycles that `InodeStore::drop()` explicitly clears.
- Used by `proc_paths.rs` and serialization to traverse and preserve inode relationships.

Edge cases and risks:
- Lock ordering matters: dropping `StrongInodeReference` while holding the store lock can deadlock unless `drop_unlocked()` is used.
- Refcounts intentionally saturate on over-forget to avoid integer underflow from misbehaving guests.
- The iterator does not hold the lock across calls and can see newly added inodes with higher IDs.
