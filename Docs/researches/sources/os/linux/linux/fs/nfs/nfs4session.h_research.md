# File Research: sources/os/linux/linux/fs/nfs/nfs4session.h

This header defines NFSv4.1+ session and slot-table structures plus the public session-management interface used by NFSv4 procedure and client code.

Constants:
- Default forechannel slot table size: `NFS4_DEF_SLOT_TABLE_SIZE`.
- Default callback slot table size: `NFS4_DEF_CB_SLOT_TABLE_SIZE`.
- Maximum slot table size and slot id: `NFS4_MAX_SLOT_TABLE` and `NFS4_MAX_SLOTID`.
- Sentinel no-slot value: `NFS4_NO_SLOT`.

Main structures:
- `struct nfs4_slot` stores parent table, linked-list pointer, generation, slot number, current/last-acked/highest-sent sequence numbers, and privileged/sequence-done flags.
- `struct nfs4_slot_table` stores parent session, allocated slot list, used-slot bitmap, locks, wait queues, completion, max/server/target slot limits, derivative state for target changes, generation, and draining state.
- `struct nfs4_session` stores session id, flags, session state, SSV/hash data, forechannel/backchannel attributes, forechannel/backchannel slot tables, and parent client.

Public APIs:
- Slot table setup/shutdown: `nfs4_setup_slot_table()`, `nfs4_shutdown_slot_table()`, and `nfs4_setup_session_slot_tables()`.
- Slot allocation and lookup: `nfs4_alloc_slot()`, `nfs4_lookup_slot()`, `nfs4_try_to_lock_slot()`, `nfs4_free_slot()`, and `nfs4_slot_wait_on_seqid()`.
- Waiter assignment and wakeup: `nfs41_wake_and_assign_slot()` and `nfs41_wake_slot_table()`.
- Dynamic slot updates: `nfs41_set_target_slotid()` and `nfs41_update_target_slotid()`.
- Session lifecycle: `nfs4_alloc_session()`, `nfs4_destroy_session()`, `nfs4_init_session()`, and `nfs4_init_ds_session()`.

Inline helpers:
- `nfs4_slot_tbl_draining()` checks whether the table is draining.
- `nfs4_test_locked_slot()` tests whether a slot bit is in use.
- `nfs4_get_session()`, `nfs4_has_session()`, and `nfs4_has_persistent_session()` expose session presence and persistence.
- `nfs4_copy_sessionid()` copies session IDs.
- `nfs_session_id_hash()` computes a CRC32-derived session-id hash.

Risk areas:
- These structures are shared across the session sequencing, callback, recovery, and client lifecycle code.
- Bitmap dimensions and slot maxima must stay aligned with `NFS4_MAX_SLOT_TABLE`.
- Inline helpers encode assumptions that must match `nfs4session.c` locking and state transitions.
