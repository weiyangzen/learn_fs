# sources/user-network-fs/samba/source3/modules/vfs_commit.c

## Purpose
`vfs_commit.c` periodically commits dirty file data to stable storage to reduce data loss and smooth writeback without forcing synchronous I/O on every write.

## Important APIs, Types, And Functions
`struct commit_info` is stored as a per-fsp extension and tracks dirty bytes, threshold, EOF mode, and expected EOF. `commit_do()` calls `fdatasync()` or `fsync()` and clears dirty bytes on success. `commit_openat()` installs state for writable files based on `commit:dthresh` and `commit:eof mode`. `commit_pwrite()`, `commit_pwrite_send/recv()`, `commit_close()`, and `commit_ftruncate()` enforce commit decisions.

## Control Flow
Writable open initializes commit settings. Before the first write in EOF mode, the module stats the file to seed expected EOF. Each successful write increments dirty bytes; crossing the threshold triggers sync. Hinted EOF mode commits once when the write reaches the expected file size; growth mode updates EOF after each growth-triggered commit. Close flushes outstanding dirty data but ignores the commit result.

## State And Persistence
State is per open file and disappears on close. Persistence is only the data actually synced by fdatasync/fsync. `module_debug` is process-global and loaded on connect.

## Dependencies And Integration Points
The module uses Samba VFS fsp extensions, tevent async wrappers, `lp_parm_*`, `fsp_get_io_fd()`, and platform sync calls. It stacks above the storage implementation and delegates writes to the next VFS module.

## Risks
Async pwrite performs a blocking commit in the completion callback. Threshold comparison is `>`, not `>=`. EOF inference can be wrong for out-of-order, sparse, or concurrent writes. If the platform has no sync primitive, commit support is effectively a logged no-op. Close-time sync errors are ignored.

## Test Signals
Cover read-only opens, threshold flushes, hinted and growth EOF modes, ftruncate updating EOF, close flush, fsync/fdatasync failure propagation on writes, async pwrite behavior, and disabled configuration.
