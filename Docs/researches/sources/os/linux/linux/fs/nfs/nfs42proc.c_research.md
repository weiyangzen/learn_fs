# File Research: sources/os/linux/linux/fs/nfs/nfs42proc.c

This file implements the NFSv4.2 client procedure layer for operations beyond baseline NFSv4: `ALLOCATE`, `DEALLOCATE`, `ZERO_RANGE`, server-side `COPY`, `COPY_NOTIFY`, `OFFLOAD_CANCEL`, `OFFLOAD_STATUS`, sparse-file `SEEK`, pNFS `LAYOUTSTATS` and `LAYOUTERROR`, `CLONE`, and NFSv4.2 user extended attributes.

Key responsibilities:
- Converts VFS-facing operations into NFSv4.2 compound RPCs through `nfs4_call_sync()` or async `rpc_run_task()`.
- Selects and validates open/lock stateids with `nfs4_set_rw_stateid()`.
- Routes protocol errors through `nfs4_handle_exception()` and async errors through `nfs4_async_handle_error()`.
- Updates inode attributes, change attributes, delegation timestamps, and page cache state after server-side mutation.
- Clears server capability bits when operations return unsupported results.

Important flows:
- Fallocate family:
  - `_nfs42_proc_fallocate()` builds common fallocate args/results, requests cache-consistency attributes, sends the compound, traces it, removes SUID-related cache state when needed, and applies weak cache consistency updates.
  - `nfs42_proc_allocate()`, `nfs42_proc_deallocate()`, and `nfs42_proc_zero_range()` serialize write-side mutations with `nfs_start_io_write()` / `nfs_end_io_write()`, perform cache truncation/invalidation, and downgrade unsupported capabilities.
- Server-side copy:
  - `_nfs42_proc_copy()` flushes source writeback, blocks destination direct I/O, syncs the destination inode, sets source/destination stateids, sends `COPY`, verifies write/commit verifiers, handles async copy completion, commits unstable copy results, and updates destination cache state.
  - `handle_async_copy()` joins callback-completed copy state or registers pending copy state, waits with exponential timeout bounded by lease time, polls `OFFLOAD_STATUS`, restarts/cancels when required, and translates server copy failures into fallback-oriented errors.
  - `nfs42_proc_copy()` serializes destination copy with `inode_lock()`, handles source and destination recovery exceptions separately, responds to `OFFLOAD_NO_REQS` by switching sync mode, and triggers offload cancellation for inter-server failure cases.
  - `nfs42_proc_copy_notify()` builds inter-server source authorization, including a destination `NL4_NETADDR`, then returns the copy-notify stateid and source server list.
- Offload helpers:
  - `nfs42_do_offload_cancel_async()` sends async `OFFLOAD_CANCEL` using sequence callbacks and removes `NFS_CAP_OFFLOAD_CANCEL` if unsupported.
  - `nfs42_proc_offload_status()` polls async copy progress and maps copy stateid failures to `-EBADF` instead of broad state recovery.
- Sparse and clone operations:
  - `nfs42_proc_llseek()` implements `SEEK_HOLE` / `SEEK_DATA` through NFSv4.2 `SEEK`, mapping unsupported protocol status to `-EOPNOTSUPP`.
  - `nfs42_proc_clone()` wraps `CLONE`, sets read/write stateids, updates destination page cache and attributes, and clears clone capability on unsupported results.
- pNFS telemetry:
  - `nfs42_proc_layoutstats_generic()` asynchronously reports layout I/O stats while holding active inode/layout references until release.
  - `nfs42_proc_layouterror()` asynchronously reports layout/device errors, invalidates layout stateids on bad/revoked stateid classes, retries old stateids when appropriate, and clears `NFS_CAP_LAYOUTERROR` when unsupported.
- Extended attributes:
  - `nfs42_proc_getxattr()`, `nfs42_proc_setxattr()`, `nfs42_proc_listxattrs()`, and `nfs42_proc_removexattr()` implement NFSv4.2 user xattr RPCs with retry loops, page-backed buffers, xattr cache population/removal, and change-attribute updates.

Dependencies:
- Uses `nfs42.h` for operation-specific argument/result structures and xattr sizing.
- Uses `nfs4_fs.h` for stateid helpers, exception handling, procedure declarations, and xattr cache APIs.
- Uses `nfs4session.h` for sequence setup/completion.
- Uses `pnfs.h` for layout headers, layout segments, and pNFS state invalidation.
- Integrates with `delegation.h`, `internal.h`, `iostat.h`, and `nfs4trace.h`.

Concurrency and lifetime notes:
- Copy callback state is linked on client lists protected by `cl_lock`.
- Server-side copy sets `NFS_CLNT_SRC_SSC_COPY_STATE` and `NFS_CLNT_DST_SSC_COPY_STATE` on open states while the RPC is active.
- Async RPC payloads for offload cancel, layoutstats, and layouterror are freed by `rpc_call_ops` release callbacks.
- Layoutstats clears `NFS_INO_LAYOUTSTATS` with memory barriers after releasing layout-driver private data.
- Layouterror holds both an active inode reference and a pNFS layout segment reference.
- Fallocate paths use write-side NFS I/O serialization; copy uses destination inode locking.

Risk areas:
- Async server-side copy has subtle transitions between callback completion, polling, cancellation, restart, verifier validation, and VFS fallback.
- Correct page-cache invalidation is essential after allocate, deallocate, zero range, copy, and clone.
- Error translation deliberately distinguishes `-ENOTSUPP`, `-EOPNOTSUPP`, protocol status codes, and fallback-triggering errors.
- pNFS layoutstats/layouterror recovery depends on comparing layout stateids under inode lock and committing dirty data before retrying.
- Several async task-creation error paths return directly after allocating callback data; ownership must remain consistent with RPC setup expectations.
