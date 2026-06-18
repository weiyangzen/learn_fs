# File Research: sources/os/linux/linux-stable/fs/smb/server/oplock.c

This file implements ksmbd oplock and SMB2/SMB3 lease handling: allocation, reference management, lease tables, break notification, grant decisions on open, parent lease breaks, create-context parsing, durable-handle validation, and response context construction.

Global state:
- `lease_table_list`: global list of lease tables keyed by client GUID.
- `lease_list_lock`: rwlock protecting the global lease table list.

Object lifecycle:
- `alloc_opinfo()`
  - Allocates `struct oplock_info`, records session, gets a connection reference, initializes wait queues, list nodes, refcount, breaking counter, fid, tree id, and default level/state.
- `alloc_lease()`, `free_lease()`
  - Allocate and copy lease state from `lease_ctx_info`.
- `free_opinfo()` / `free_opinfo_rcu()`
  - Free oplock info via RCU and release the connection reference.
- `opinfo_get()`
  - RCU-safe lookup from `ksmbd_file->f_opinfo`.
- `opinfo_get_list()`
  - Gets first oplock info from an inode’s `m_op_list` under `ci->m_lock`.
- `opinfo_put()`
  - Atomic refcount release.
- `opinfo_add()`, `opinfo_del()`
  - Add/remove oplock info from inode list; lease entries are also removed from lease tables.
- `opinfo_count()`, `opinfo_count_inc()`, `opinfo_count_dec()`
  - Track ordinary oplocks versus stream oplocks through inode counters.

Lease-table management:
- `alloc_lease_table()`
  - Allocates a table for a connection client GUID.
- `lease_add_list()`, `lease_del_list()`
  - Add/remove opinfo from a lease table’s RCU list.
- `add_lease_global_list()`
  - Reuses an existing client-GUID lease table or publishes a new one.
- `destroy_lease_table()`
  - Destroys all lease tables, or only tables matching a connection’s client GUID.

State transitions:
- `opinfo_write_to_read()`: batch/exclusive to level II.
- `opinfo_read_handle_to_read()`: read+handle lease to read.
- `opinfo_write_to_none()`: batch/exclusive to none.
- `opinfo_read_to_none()`: level II to none.
- `lease_read_to_write()`: upgrade read lease to include write caching and set oplock level accordingly.
- `lease_none_upgrade()`: upgrade a none lease to a requested lease state and derive oplock level.
- `set_oplock_level()` dispatches grant to write/read/none helpers.

Break handling:
- `wait_for_break_ack()`
  - Waits up to `OPLOCK_WAIT_TIME` for state to become none or closing; timeout forces lease/oplock to none.
- `oplock_break_pending()`
  - Serializes concurrent breaks with `pending_break` bit wait/wake.
- `smb2_oplock_break_noti()` and `__smb2_oplock_break_noti()`
  - Build and send SMB2 oplock break notifications.
- `smb2_lease_break_noti()` and `__smb2_lease_break_noti()`
  - Build and send SMB2 lease break notifications.
- `wait_lease_breaking()`
  - Waits briefly for lease break counter to drain.
- `oplock_break()`
  - Core break state machine. Determines lease new state, optionally sends interim response, marks ACK wait, sends notification, wakes pending breakers, and waits for lease-breaking completion.

Open/grant path:
- `same_client_has_lease()`
  - Finds an existing lease with the same client GUID and lease key on the same inode; may upgrade the existing lease state.
- `find_same_lease_key()`
  - Rejects reuse of the same lease key by the same client on another file.
- `smb_grant_oplock()`
  - Main grant decision on file open.
  - Handles directory lease restrictions, lease allocation, no-existing-oplock fast path, attribute-only/truncate cases, same-client lease reuse, previous oplock breaking, share-mode failures, mixed lease/oplock cases, lease-table preallocation, inode-list publication, global lease-list publication, and `fp->f_opinfo` RCU assignment.

Break-all helpers:
- `smb_break_all_write_oplock()`
  - Breaks a batch/exclusive oplock to level II.
- `smb_break_all_levII_oplock()`
  - Breaks level II oplocks/read leases to none, with same-lease-owner skip logic.
- `smb_break_all_oplock()`
  - Breaks both write and level II oplocks.

Parent lease handling:
- `smb_send_parent_lease_break_noti()`
  - For v2 leases, breaks leases on the parent directory unless the request supplies a matching parent lease key.
- `smb_lazy_parent_lease_break_close()`
  - On close, lazily breaks parent directory leases for v2 lease cases.

Create-context helpers:
- `smb2_map_lease_to_oplock()`
  - Maps lease state bits to SMB2 oplock level.
- `create_lease_buf()`
  - Builds lease response context for v1 or v2 lease.
- `parse_lease_state()`
  - Finds and parses the `RqLs` create context into `lease_ctx_info`.
- `smb2_find_context_vals()`
  - Iterates create contexts, validating alignment, offsets, names, data lengths, and `Next`.
- Response builders:
  - `create_durable_rsp_buf()`
  - `create_durable_v2_rsp_buf()`
  - `create_mxac_rsp_buf()`
  - `create_disk_id_rsp_buf()`
  - `create_posix_rsp_buf()`

Lookup and durable reconnect:
- `lookup_lease_in_table()`
  - Finds a lease by client GUID and lease key while requiring active break-related state and handle/write caching.
- `smb2_check_durable_oplock()`
  - Validates durable reconnect ownership, client GUID, lease key, handle-caching state, lease version, and name reconnect validity.

Concurrency:
- Uses RCU for `fp->f_opinfo` and lease-list traversal.
- Uses `ci->m_lock` for inode oplock lists.
- Uses `lease_list_lock` for global lease table list.
- Uses per-lease-table spinlocks for `lease_list`.
- Uses wait queues and atomic counters for break acknowledgement and lease-breaking coordination.
- Uses connection refcounts to keep notification targets alive.

Risk areas:
- This is one of the most concurrency-sensitive ksmbd files: oplock info is published through both inode lists and RCU file pointers, while lease entries are also globally visible.
- `smb_grant_oplock()` intentionally preallocates lease tables and sets `opinfo->o_fp` before publication; comments indicate this order prevents NULL dereference by concurrent lease-key scans.
- Break state transitions involve timeouts that force state to none; changing timeout or ACK handling can affect client cache coherency and data consistency.
- `create_durable_v2_rsp_buf()` zeroes `sizeof(struct create_durable_rsp)` while using `struct create_durable_rsp_v2`; this may be intentional layout overlap, but it is a notable structure-size dependency.
- `create_disk_id_rsp_buf()` uses `offsetof(struct create_mxac_rsp, Name)` for `create_disk_id_rsp`; this cross-structure offset dependency should remain layout-compatible.
