# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4session.h

This header defines NFSv4.1+ session and slot-table data structures and declares the slot/session helper APIs.

Constants:
- `NFS4_DEF_SLOT_TABLE_SIZE` = 64
- `NFS4_DEF_CB_SLOT_TABLE_SIZE` = 16
- `NFS4_MAX_SLOT_TABLE` = 1024
- `NFS4_MAX_SLOTID`
- `NFS4_NO_SLOT`

Structures:
- `struct nfs4_slot`
  - Parent table, linked-list next pointer, generation, slot number, sequence numbers, privileged flag, and sequence-done flag.
- `struct nfs4_slot_table`
  - Parent session, slot list, used-slot bitmap, lock, RPC wait queue, sequence wait queue, max/highest slot fields, target/server slot fields, derivative tracking, completion, and state bits.
- `struct nfs4_session`
  - Session ID, flags, session state, hash/SSV fields, forechannel/backchannel attributes and slot tables, and parent client.

Enums:
- Slot table state:
  - `NFS4_SLOT_TBL_DRAINING`
- Session state:
  - `NFS4_SESSION_INITING`
  - `NFS4_SESSION_ESTABLISHED`

Declared APIs:
- Slot table setup/shutdown, allocation, lookup, locking, freeing, waiting, wake/assign.
- Target slotid update and dynamic resize helpers.
- Session slot table setup, allocation, destruction, initialization, and DS initialization.

Inline helpers:
- `nfs4_slot_tbl_draining()`
- `nfs4_test_locked_slot()`
- `nfs4_get_session()`
- `nfs4_has_session()`
- `nfs4_has_persistent_session()`
- `nfs4_copy_sessionid()`
- `nfs_session_id_hash()`

Role:
- Shared contract between session management, sequence processing, callback handling, and NFSv4.2 procedure code.

Risk areas:
- `SLOT_TABLE_SZ` must be large enough for the maximum slot table bitmap.
- Inline state checks are widely used; semantic changes affect session recovery, callback routing, and RPC scheduling.
