# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4session.c

This file implements NFSv4.1+ session slot-table management and session lifecycle helpers.

Slot table basics:
- `nfs4_init_slot_table()` initializes lock, wait queues, completion, and highest-used state.
- Slots are linked in a list and tracked in a bitmap.
- `nfs4_alloc_slot()` finds a free bitmap slot up to `max_slotid`, creates the slot if needed, marks it used, and updates highest-used slot id.
- `nfs4_free_slot()` clears a used slot and recalculates `highest_used_slotid`, completing drain when no slots remain.
- `nfs4_lookup_slot()` returns an existing or newly created slot if within max slot id.
- `nfs4_try_to_lock_slot()` marks a specific slot used if available.

Slot sequence wait:
- `nfs4_slot_seqid_in_use()` checks whether a slot/sequence pair is still in flight.
- `nfs4_slot_wait_on_seqid()` waits for that sequence to complete, primarily for callback channel coordination.

Sizing and reset:
- `nfs4_grow_slot_table()` ensures enough slots exist.
- `nfs4_shrink_slot_table()` frees retired slots above new size.
- `nfs4_reset_slot_table()` resets sequence numbers and slot limits.
- `nfs4_realloc_slot_table()` grows/resets table with a cap at `NFS4_MAX_SLOT_TABLE`.
- `nfs41_set_target_slotid()` and `nfs41_update_target_slotid()` adapt client target slot limits based on server SEQUENCE replies.
- Outlier filtering uses first and second derivative tracking to avoid abrupt target-slot changes.

RPC wait queue integration:
- `nfs41_assign_slot()` attaches an allocated slot to RPC sequence args/results unless draining and non-privileged.
- `nfs41_wake_and_assign_slot()` wakes one waiter with a specific slot.
- `nfs41_wake_slot_table()` allocates and assigns slots to waiting tasks until no more work can be woken.

Session lifecycle:
- `nfs4_alloc_session()` allocates a session and initializes forechannel/backchannel slot tables.
- `nfs4_setup_session_slot_tables()` initializes or resets forechannel and backchannel tables using negotiated channel attributes.
- `nfs4_destroy_session()` sends `DESTROY_SESSION`, destroys backchannel, releases slot tables, and frees session.
- `nfs4_init_session()` clears initializing state and checks readiness.
- `nfs4_init_ds_session()` initializes DS session lease timing from MDS lease and verifies DS role.

Risk areas:
- Slot-table locks protect bitmap, highest-used, and dynamic sizing fields.
- Drain completion depends on accurate `highest_used_slotid` maintenance.
- Dynamic resizing must respect server highest slot id, target highest slot id, and local maximum.
- Session readiness maps some initialization failures to `-EPROTONOSUPPORT` to allow fallback to other NFS versions.
