# File Research: sources/os/linux/linux-stable/fs/smb/client/misc.c

Read status: complete.

## Purpose

Provides shared CIFS client utility routines for xid accounting, session/tcon allocation, SMB buffer pools, oplock and writer coordination, deferred close handling, delete-handle marking, DFS referral parsing, DFS superblock lookup, DFS helper checks, and reconnect waiting.

## Main Responsibilities

- Allocate/free core session and tree-connect objects.
- Allocate/release CIFS large and small SMB buffers from mempools.
- Maintain xid active counters used for tracing VFS requests.
- Set oplock/cache flags and coordinate writers with pending oplock breaks.
- Queue and complete oplock break work.
- Track backup-credential eligibility.
- Manage pending opens and deferred closes.
- Force-close deferred files globally, per-superblock, per-inode, or under a dentry.
- Mark open handles as deleted so close deferral is not used after unlink/rename.
- Parse DFS referral V3 responses into internal target arrays.
- Find CIFS superblocks associated with DFS tcons.
- Resolve and compare DFS target host IPs.
- Update DFS prepaths and detect special DFS-link error cases.
- Wait for reconnect completion under hard/soft mount semantics.

## Important Functions

- `_get_xid()` / `_free_xid()`
  - Increment/decrement global active xid counters and allocate monotonically increasing xid values.

- `sesInfoAlloc()` / `sesInfoFree()`
  - Initialize or release `struct cifs_ses`, including locks, lists, iface refs, NLS table, passwords, names, domain fields, and auth key material.

- `tcon_info_alloc()` / `tconInfoFree()`
  - Initialize or release `struct cifs_tcon`, including cached directory state, counters, locks, lists, stats timestamps, fscache lock, pending opens, query interface work, and DFS cache work.

- `cifs_buf_get()` / `cifs_buf_release()` / `cifs_small_buf_get()` / `cifs_small_buf_release()` / `free_rsp_buf()`
  - Manage large and small SMB request/response buffers and allocation counters.

- `cifs_autodisable_serverino()`
  - Clears `CIFS_MOUNT_SERVER_INUM`, records autodisable state, and emits warnings when server inode numbers are unreliable.

- `cifs_set_oplock_level()`
  - Maps protocol oplock level into CIFS read/write cache flags.

- `cifs_get_writer()` / `cifs_put_writer()`
  - Block writers while an oplock break is pending and wake oplock-break waiters when writers drain.

- `cifs_queue_oplock_break()` / `cifs_done_oplock_break()`
  - Reference the open file, queue break work, and clear/wake pending break state.

- `backup_cred()`
  - Checks backup uid/gid mount options against current credentials.

- `cifs_add_pending_open*()` / `cifs_del_pending_open()`
  - Track pending opens by lease key under tcon open-file locking.

- `cifs_is_deferred_close()` / `cifs_add_deferred_close()` / `cifs_del_deferred_close()`
  - Manage per-inode deferred close records under `deferred_lock`.

- `cifs_close_deferred_file()` / `cifs_close_all_deferred_files()` / `cifs_close_all_deferred_files_sb()` / `cifs_close_deferred_file_under_dentry()`
  - Cancel delayed close work and drop file refs immediately in several scopes.

- `cifs_mark_open_handles_for_deleted_file()`
  - Marks matching open handles deleted, comparing paths only when hardlinks require precision.

- `parse_dfs_referrals()`
  - Validates DFS referral response bounds, requires referral version 3, converts paths from UTF-16 or byte form, and fills `dfs_info3_param` entries.

- `extract_unc_hostname()` / `copy_path_name()`
  - Small path utility helpers for UNC host extraction and bounded path copying.

- `cifs_get_dfs_tcon_super()` / `cifs_put_tcp_super()`
  - Locate and hold/release an active superblock matching a DFS tcon’s origin path.

- `match_target_ip()` / `cifs_update_super_prepath()` / `cifs_inval_name_dfs_link_error()`
  - DFS upcall helpers for DNS target matching, prepath replacement, and probing whether `STATUS_OBJECT_NAME_INVALID` is actually a DFS link case.

- `cifs_wait_for_server_reconnect()`
  - Waits for reconnect state to clear, scaling timeout by target count and retrying only for hard-style behavior.

## Dependencies

- Uses CIFS core global counters, mempools, cached directory subsystem, DFS cache/upcall code when enabled, DNS resolution, SMB1/SMB2 protocol helpers, Linux superblock iteration, wait queues, delayed work, spinlocks, mutexes, and krefs.

## Notable Behaviors

- Deferred close cancellation builds a temporary list under locks, then drops file refs outside the main open-file lock.
- DFS referral parsing includes explicit response-size and offset-bound checks before string extraction.
- `cifs_close_all_deferred_files_sb()` takes temporary tcon references while walking the superblock tlink tree.
- Reconnect wait returns `-ERESTARTSYS` on signal and `-EHOSTDOWN` when a soft wait gives up.
