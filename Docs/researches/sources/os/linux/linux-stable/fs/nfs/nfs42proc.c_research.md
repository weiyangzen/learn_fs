# File Research: sources/os/linux/linux-stable/fs/nfs/nfs42proc.c

This file implements the NFSv4.2 client-side procedure layer for operations above the basic NFSv4 protocol: `ALLOCATE`, `DEALLOCATE`, `ZERO_RANGE`, `COPY`, `COPY_NOTIFY`, `OFFLOAD_CANCEL`, `OFFLOAD_STATUS`, `SEEK`, pNFS `LAYOUTSTATS` / `LAYOUTERROR`, `CLONE`, and user xattr RPC wrappers.

Key responsibilities:
- Converts VFS-facing operations into NFSv4.2 compound RPC calls through `nfs4_call_sync()` or async `rpc_run_task()`.
- Acquires correct open/lock stateids with `nfs4_set_rw_stateid()`.
- Routes NFSv4 state recovery through `nfs4_handle_exception()`.
- Maintains local page cache and inode metadata after server-side mutation.
- Degrades server capability bits when operations return unsupported errors.

Important flows:
- Fallocate family:
  - `_nfs42_proc_fallocate()` builds shared fallocate RPC args/results and updates inode attributes.
  - `nfs42_proc_allocate()`, `nfs42_proc_deallocate()`, and `nfs42_proc_zero_range()` wrap capability checks, write serialization, page-cache truncation/invalidation, and capability fallback.
- Server-side copy:
  - `nfs42_proc_copy()` drives retry and exception handling for intra-server and inter-server copy.
  - `_nfs42_proc_copy()` flushes source writes, syncs destination, sets source/destination stateids, sends `COPY`, optionally verifies commit verifiers, waits for async completion, and updates destination cache state.
  - `handle_async_copy()` manages callback-completed copy state, timeout polling via `OFFLOAD_STATUS`, restart/cancel logic, and translated completion errors.
  - `nfs42_proc_copy_notify()` prepares inter-server copy source authorization and server location data.
- Clone:
  - `nfs42_proc_clone()` validates capability and state, then `_nfs42_proc_clone()` sends `CLONE`, updates destination size/cache, and refreshes attributes.
- SEEK:
  - `nfs42_proc_llseek()` implements `SEEK_HOLE` / `SEEK_DATA` with NFSv4.2 `SEEK`, falling back to `-EOPNOTSUPP` for callers.
- pNFS telemetry:
  - `nfs42_proc_layoutstats_generic()` asynchronously reports layout device I/O stats.
  - `nfs42_proc_layouterror()` asynchronously reports layout/device errors and handles bad/old layout stateids.
- Extended attributes:
  - `nfs42_proc_getxattr()`, `nfs42_proc_setxattr()`, `nfs42_proc_listxattrs()`, and `nfs42_proc_removexattr()` wrap NFSv4.2 xattr operations, retry on recoverable state/session errors, update change attributes, and populate or invalidate the xattr cache.

Notable dependencies:
- `nfs42.h` for operation argument/result structures.
- `nfs4_fs.h` for stateid, exception, and NFSv4 procedure declarations.
- `nfs4session.h` for sequence/session handling.
- `pnfs.h` for layout state and pNFS segment references.
- `delegation.h`, `internal.h`, `iostat.h`, and `nfs4trace.h`.

Concurrency and lifetime notes:
- Copy callback state is linked on client lists protected by `cl_lock`.
- Async RPC data for offload, layoutstats, and layouterror is released through `rpc_call_ops`.
- Layoutstats holds active inode/layout references until release.
- Layouterror holds both an active inode reference and pNFS layout segment reference.
- `inode_lock()` protects destination copy operations in `nfs42_proc_copy()`.
- `nfs_start_io_write()` / `nfs_end_io_write()` serialize fallocate-style write mutations.

Risk areas:
- Server-side copy has several subtle transitions between callback completion, polling, cancellation, fallback, and retry.
- Correct page-cache invalidation is essential after clone/copy/zero/deallocate.
- `-ENOTSUPP`, `-EOPNOTSUPP`, and NFS protocol errors are intentionally translated in different paths; changing these translations can affect VFS fallback behavior.
- pNFS layout error/stat paths rely on stateid comparison to decide whether to invalidate layouts or retry.
