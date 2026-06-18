# File Research: sources/os/linux/linux/fs/nfs/file.c

## Role

`file.c` is the NFS regular-file VFS bridge. It provides file operations, address-space operations, mmap behavior, cached read/write paths, direct-I/O dispatch, fsync/commit integration, swapfile hooks, and lock/flock handling.

Main exported surfaces include `nfs_file_operations`, `nfs_file_aops`, `nfs_check_flags()`, `nfs_file_release()`, `nfs_file_llseek()`, `nfs_file_read()`, `nfs_file_splice_read()`, `nfs_file_mmap_prepare()`, `nfs_file_fsync()`, `nfs_truncate_last_folio()`, `nfs_file_write()`, `nfs_lock()`, and `nfs_flock()`.

## Open, Release, Seek, Flush

`nfs_check_flags()` rejects `O_APPEND | O_DIRECT`, because NFS direct writes do not provide atomic append semantics.

`nfs_file_open()` updates stats, checks flags, calls `nfs_open()`, and enables `FMODE_CAN_ODIRECT` on success. `nfs_file_release()` clears the open context and releases fscache file state.

`nfs_file_llseek()` revalidates file size for `SEEK_END`, `SEEK_DATA`, and `SEEK_HOLE`, then uses `generic_file_llseek()`.

`nfs_file_flush()` writes back dirty pages for writable files and reports writeback errors sampled from the mapping.

## Cached And Direct Reads

`nfs_file_read()` dispatches `IOCB_DIRECT` to `nfs_file_direct_read()`. Cached reads call `nfs_start_io_read()`, revalidate the mapping, use `generic_file_read_iter()`, update normal read byte stats, and call `nfs_end_io_read()`.

`nfs_file_splice_read()` follows the same revalidation and I/O exclusion pattern around `filemap_splice_read()`.

## Mmap And Folio Operations

`nfs_file_mmap_prepare()` calls `generic_file_mmap_prepare()`, installs `nfs_file_vm_ops`, and revalidates the mapping.

`nfs_vm_page_mkwrite()` handles shared writable mmap faults. It waits for fscache/private state, waits for invalidation, locks the folio, waits for writeback, verifies mapping and page length, flushes incompatible state, and calls `nfs_update_folio()`. Failure maps to `VM_FAULT_SIGBUS`.

`nfs_file_aops` wires NFS read/write helpers into the page cache: `read_folio`, `readahead`, `writepages`, `write_begin`, `write_end`, invalidation, release, migration, laundering, dirty/writeback classification, swap hooks, and direct swap I/O.

## Cached Writes

`nfs_write_begin()` truncates the last folio when extending past EOF, obtains a write folio, flushes incompatible pending state, and may perform read-modify-write if a partial non-uptodate folio should be read first. That decision is controlled by `nfs_want_read_modify_write()` and pNFS layout requirements.

`nfs_write_end()` zeroes uninitialized folio regions when extending, calls `nfs_update_folio()`, unlocks/releases the folio, updates write stats, and flushes all writes if the open context key is expiring.

`nfs_file_write()` dispatches direct writes to `nfs_file_direct_write()`. Cached writes reject active swapfiles, revalidate file size for append or writes past local EOF, clear invalid mapping state, start write exclusion, run `generic_write_checks()` and `generic_perform_write()`, honor eager/wait mount options, call `generic_write_sync()`, and report writeback errors such as quota, file too large, or no space.

## Fsync And Commit

`nfs_file_fsync()` loops until dirty writeback, NFS commits, pNFS sync, and redirtied-page accounting stabilize. `nfs_file_fsync_commit()` calls `nfs_commit_inode()` and advances writeback error state.

## Swapfile Support

`nfs_swap_activate()` rejects sparse swapfiles by comparing blocks to file size, activates RPC swap behavior, installs a single swap extent, optionally calls protocol `enable_swap()`, and marks `SWP_FS_OPS`. `nfs_swap_deactivate()` reverses RPC/protocol swap state.

## Locking

`nfs_lock()` handles POSIX byte-range locks. It rejects reclaim, optionally validates protocol lock bounds, checks local conflicts first for GETLK, uses server locking unless local locking mount flags apply, flushes writes before unlock/setlk, waits for direct I/O counters on unlock, and treats successful locks as cache-coherency points by syncing/zapping/revalidating mappings unless a delegation protects the file.

`nfs_flock()` implements flock semantics through local or server POSIX-style locks, depending on mount flags.
