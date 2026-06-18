# sources/user-network-fs/libnfs/lib/libnfs-sync.c

## Purpose

`libnfs-sync.c` implements the blocking, POSIX-like libnfs API on top of the library's asynchronous NFS and RPC operations. It lets callers use functions such as `nfs_mount`, `nfs_open`, `nfs_read`, `nfs_write`, `nfs_stat64`, `nfs_opendir`, `nfs_rename`, and ACL/export discovery helpers without manually polling the RPC file descriptor. The file is mostly a synchronization facade: each synchronous function initializes callback state, starts the corresponding `*_async` operation, waits until the callback marks completion, translates callback data into the caller's output buffers, and returns a libnfs status or negative errno.

## Important APIs, Types, and Functions

The central type is `struct sync_cb_data`, which records `is_finished`, `status`, `offset`, generic `return_data`, integer scratch `return_int`, a call name used in diagnostics, and, when `HAVE_MULTITHREADING` is enabled, a per-call semaphore. `nfs_init_cb_data` initializes this state and, in multithreaded mode, maps the caller to a per-thread `struct nfs_context` clone hanging off `nfsi->thread_ctx`. `cb_data_is_finished` records status and wakes the semaphore. `wait_for_nfs_reply` waits on the NFS context by either blocking on the semaphore when the service thread is active or by polling `nfs_get_fd` and dispatching `nfs_service`. `wait_for_reply` performs the same loop for raw `struct rpc_context` operations such as mount export listing.

The public synchronous wrappers cover mount lifecycle (`nfs_mount`, `nfs_umount`), metadata (`nfs_stat`, `nfs_stat64`, `nfs_lstat64`, `nfs_fstat`, `nfs_fstat64`, `nfs_statvfs`, `nfs_statvfs64`), file handles (`nfs_open`, `nfs_open2`, `nfs_creat`, `nfs_close`), I/O (`nfs_pread`, `nfs_read`, `nfs_preadv`, `nfs_readv`, `nfs_pwrite`, `nfs_write`, `nfs_fsync`), file sizing (`nfs_ftruncate`, `nfs_truncate`), namespace mutation (`nfs_mkdir`, `nfs_mkdir2`, `nfs_rmdir`, `nfs_mknod`, `nfs_unlink`, `nfs_symlink`, `nfs_rename`, `nfs_link`), directory open (`nfs_opendir`), offset/lock operations (`nfs_lseek`, `nfs_lockf`, `nfs_fcntl`), permissions and ownership (`nfs_chmod`, `nfs_lchmod`, `nfs_fchmod`, `nfs_chown`, `nfs_lchown`, `nfs_fchown`), times (`nfs_utimes`, `nfs_lutimes`, `nfs_utime`), access checks (`nfs_access`, `nfs_access2`), symlink reads (`nfs_readlink`, `nfs_readlink2`), and ACL helpers (`nfs3_getacl`, `nfs4_getacl`, `nfs3_acl_free`, `nfs4_acl_free`).

Outside mounted file operations, the file also provides mount daemon export enumeration through `mount_getexports_mountport`, `mount_getexports_timeout`, `mount_getexports`, and `mount_free_export_list`. When `NO_SRV_AUTOSCAN` is not defined, `nfs_find_local_servers` sends UDP portmapper CALLIT probes on broadcast interfaces and returns a deduplicated `nfs_server_list`.

## Control Flow

The common wrapper flow is: fill any `sync_cb_data` output pointers, call `nfs_init_cb_data`, submit the async request, wait for callback completion, destroy the semaphore if present, and return `cb_data.status`. Each callback handles only operation-specific result transfer, such as copying `struct stat`, assigning a returned `struct nfsfh *`, duplicating a readlink string, copying `struct statvfs`, or deep-copying NFSv4 ACL entries.

Mounting uses `_nfs_mount` to submit `nfs_mount_async`, wait, clear `rpc->connect_cb`, and disconnect on failure. Public `nfs_mount` first tries the default NFSv3 path and, if it fails while `default_version` is still set, clears the v3 root file handle, switches `nfsi->version` to `NFS_V4`, disconnects, and retries. `nfs_umount` is similar but treats the expected `-EIO` from the v3 disconnect path as success. `nfs_open` retries up to ten times on `-EIO`, which is a targeted recovery path for reconnectable open failures.

The raw RPC export flow initializes an independent `rpc_context`, optionally sets mount port or timeout, submits `mount_getexports_async`, waits with `wait_for_reply`, destroys the RPC context, and returns a newly allocated linked list. Server discovery binds a UDP RPC context to `0.0.0.0`, enumerates IPv4 broadcast-capable non-loopback interfaces, sends three rounds of portmapper CALLIT probes for the mount program, polls for about one second per round, and appends unique source addresses observed in `callit_cb`.

## State and Persistence Behavior

The file does not persist data outside process memory. Its short-lived state is `sync_cb_data` on the caller's stack plus callback-produced heap allocations returned to the caller. The caller owns `struct nfsfh *`, `struct nfsdir *`, duplicated readlink buffers from `nfs_readlink2`, export lists, server lists, and ACL allocations, and must free them with the corresponding libnfs APIs.

Multithreaded synchronous calls are stateful at the `nfs_context_internal` level. `nfs_init_cb_data` may allocate a `struct nfs_thread_context`, copy the master `nfs_context`, set `master_ctx`, and store per-thread error strings so synchronous callers can block on semaphores while a shared service thread drives the single RPC context. This means context destruction must later release those thread contexts, and errors are deliberately thread-local for callers but RPC transport state remains shared.

## Dependencies and Integration Points

This file depends on `libnfs.c` for public async dispatchers and context utilities, on `nfs_v3.c` and `nfs_v4.c` through the `nfs_*_async` APIs, and on the lower RPC layer for `rpc_get_fd`, `rpc_which_events`, `rpc_service`, `rpc_disconnect`, `rpc_current_time`, and mount/portmapper helpers. Platform integration is through `poll`, socket/interface headers, `ioctl(SIOCGIFCONF/SIOCGIFFLAGS/SIOCGIFBRDADDR)` on Unix-like systems, and `WSAIoctl(SIO_GET_INTERFACE_LIST)` on Windows. `multithreading.c` supplies `nfs_mt_get_tid`, mutexes, and semaphores.

## Risks and Edge Cases

The blocking wait paths depend on callbacks always calling `cb_data_is_finished`; missed callbacks cause synchronous callers to wait until timeout or forever when no timeout applies. In the non-service-thread path, `poll` or `nfs_service` failure maps to `-EIO`, and `wait_for_nfs_reply` also cancels outstanding PDUs on service failure. In the service-thread path, the synchronous caller waits only on the semaphore, so correctness depends on the background thread continuously polling and posting completion.

Several wrappers return immediately with `-1` when async submission fails, but async readonly errors often call the callback with `-EROFS` and return `0`; callers must distinguish submission failure from operation failure. `readlink_cb` uses `strlen(data) > bufsize`, allowing a string exactly equal to `bufsize` to copy `bufsize + 1` bytes including the NUL terminator; boundary tests should cover this. `nfs4_getacl_cb` allocates each ACE name and must free partially built ACLs on allocation failure. `mount_getexports_cb` does not check every allocation result before dereference. Server discovery is IPv4 broadcast-oriented and excludes loopback and non-broadcast interfaces, so it will not discover IPv6-only or routed-only servers.

## Test Signals

Useful signals are integration tests that mount NFSv3 and NFSv4 exports, exercise every synchronous wrapper against success and server-side errno failures, and verify callbacks unblock both poll-driven and service-thread modes. Regression tests should cover v3-to-v4 mount fallback, `nfs_umount` disconnect handling, open retry on transient `-EIO`, readonly operations through the sync layer, short reads across EOF, read/write vector calls, `nfs_readlink` buffer boundaries, ACL allocation/free paths, export-list ownership, and local server discovery with duplicate CALLIT replies. Fault-injection tests should simulate poll failure, socket close, async submission failure, timeout, and allocation failure in ACL/export duplication.
