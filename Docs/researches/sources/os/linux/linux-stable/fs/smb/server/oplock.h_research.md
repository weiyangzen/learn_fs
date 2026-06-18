# File Research: sources/os/linux/linux-stable/fs/smb/server/oplock.h

This header defines oplock/lease state structures and declares the public oplock, lease, durable-handle, and create-context helper APIs.

Constants:
- `OPLOCK_WAIT_TIME`: 35 seconds.
- Oplock internal states:
  - `OPLOCK_STATE_NONE`
  - `OPLOCK_ACK_WAIT`
  - `OPLOCK_CLOSING`
- Break transition flags:
  - `OPLOCK_WRITE_TO_READ`
  - `OPLOCK_READ_HANDLE_TO_READ`
  - `OPLOCK_WRITE_TO_NONE`
  - `OPLOCK_READ_TO_NONE`

Structures:
- `struct lease_ctx_info`
  - Parsed create-context lease request: lease key, requested state, flags, duration, parent lease key, epoch, version, directory flag.
- `struct lease_table`
  - Client GUID, list of leases, global-list node, spinlock.
- `struct lease`
  - Granted/current lease state, pending new state, flags, duration, parent key, version, epoch, directory flag, owning lease table.
- `struct oplock_info`
  - Connection/session/work/file references, oplock level/state, pending break bit, fid/tid, breaking count, refcount, lease flag, truncate flag, lease pointer, inode/lease list entries, wait queues, RCU head.
- `struct lease_break_info`
  - Current/new lease state, epoch, lease key for notification.
- `struct oplock_break_info`
  - Oplock level, truncate flag, fid for notification.

Declared APIs:
- Grant/break/lifecycle:
  - `smb_grant_oplock()`
  - `smb_break_all_levII_oplock()`
  - `smb_break_all_oplock()`
  - `close_id_del_oplock()`
  - `opinfo_get()`
  - `opinfo_put()`
- State transition helpers:
  - `opinfo_write_to_read()`
  - `opinfo_read_handle_to_read()`
  - `opinfo_write_to_none()`
  - `opinfo_read_to_none()`
  - `lease_read_to_write()`
- Lease helpers:
  - `create_lease_buf()`
  - `parse_lease_state()`
  - `smb2_map_lease_to_oplock()`
  - `lookup_lease_in_table()`
  - `find_same_lease_key()`
  - `destroy_lease_table()`
  - parent lease break helpers
- Create context response helpers:
  - Durable handle, durable v2, maximal access, disk id, POSIX context builders.
- Durable reconnect:
  - `smb2_check_durable_oplock()`.

Role:
- Shared contract for SMB2 create/open, close, write/truncate, lease break ACK, durable reconnect, and create-context response paths.

Risk areas:
- `struct oplock_info` lifetime depends on RCU plus atomic refcounting; callers must pair `opinfo_get()` with `opinfo_put()`.
- `pending_break`, `breaking_cnt`, `oplock_q`, and `oplock_brk` are tightly coupled with the implementation’s break state machine.
