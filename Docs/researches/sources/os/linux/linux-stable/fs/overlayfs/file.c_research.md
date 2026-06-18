# File Research: sources/os/linux/linux-stable/fs/overlayfs/file.c

## Scope

This file implements overlayfs regular file operations by opening and caching real backing files, routing reads/writes/splice/fallocate/fsync/mmap/fadvise/copy-range/remap/flush to the correct real file, synchronizing overlay position and attributes, handling lazy upper-file open after copy-up/metacopy transitions, and enforcing flag/permission behavior.

## Public And Internal APIs Covered

- File wrapper lifecycle: `struct ovl_file`, `ovl_file_alloc()`, `ovl_file_free()`.
- Open/close: `ovl_open()`, `ovl_release()`, `ovl_open_realfile()`.
- Real-file resolution: `ovl_real_file()`, `ovl_real_file_path()`, `ovl_change_flags()`.
- File operations: `ovl_llseek()`, `ovl_read_iter()`, `ovl_write_iter()`, `ovl_splice_read()`, `ovl_splice_write()`, `ovl_fsync()`, `ovl_mmap()`, `ovl_fallocate()`, `ovl_fadvise()`, `ovl_copy_file_range()`, `ovl_remap_file_range()`, `ovl_flush()`.
- Operation table: `ovl_file_operations`.

## Control Flow And Behavior

- Open verifies lowerdata, performs copy-up if open flags require it, strips create/truncate-only flags before opening the real file, and stores the real backing file in `file->private_data`.
- `ovl_open_realfile()` checks permissions on the real inode using overlay mounter credentials, adjusts `O_NOATIME` if needed, and opens the backing file.
- `ovl_real_file_path()` detects when the originally opened real file no longer matches the current real data path, usually after copy-up or metacopy data copy-up. It lazily opens and caches an upper file with `cmpxchg_release()`.
- Flag changes are propagated to real files for append, nonblock, ndelay, and direct I/O, with immutable append and O_DIRECT capability checks.
- `llseek` keeps overlay `f_pos` as the master copy while delegating nontrivial seek semantics, including holes/data, to the real file under overlay inode lock.
- Reads and splice reads delegate through backing-file helpers with mounter credentials and atime/mtime/ctime synchronization callbacks.
- Writes, splice writes, fallocate, copy_file_range, and clone/remap operations lock the overlay inode, refresh mode/attrs, remove privileges where appropriate, operate on real files, and then refresh overlay size/timestamps.
- `fsync` only syncs upper data; lower-only objects and datasync on merge dirs avoid lower fsync to prevent read-only errors.
- Dedupe does not trigger copy-up and is rejected unless both files already have upper inodes.

## State And Data Structures

- `struct ovl_file` stores the initially opened `realfile` and an optional lazily opened `upperfile`.
- Overlay inode flags and upperdata/metacopy state decide whether the real backing file is upper, lower, or metadata-only upper.
- Uses `backing_file_ctx` callbacks for credential override and post-I/O attr updates.

## Dependencies

- Relies on overlayfs copy-up/lowerdata verification, path resolution, inode attr copy, sync policy, upperdata state, and directory real-file support.
- Uses kernel backing-file helpers, VFS I/O APIs, lease helper, fileattr privilege removal, and mounter credentials.

## Risks And Invariants

- The overlay file position must remain authoritative across backing file changes.
- Lazy upperfile caching must verify the cached file still maps to the expected upper inode, otherwise returns `-EIO`.
- Dedupe cannot copy up because that would duplicate data rather than deduplicate it.
- Write paths must update overlay metadata after backing-file operations so stat results remain coherent.
