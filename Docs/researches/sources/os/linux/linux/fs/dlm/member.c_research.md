# File Research: sources/os/linux/linux/fs/dlm/member.c

## Role

`member.c` manages DLM lockspace membership during recovery. It tracks current members, removed members, slot assignments, member weights, and communication state changes for nodes entering or leaving a lockspace.

## Slot Handling

The slot functions support lockspace slot negotiation:
- `dlm_slots_version()` checks whether a remote header supports slots.
- `dlm_slot_save()` records a member slot/generation from RCOM status.
- `dlm_slots_copy_out()` serializes current slots into an RCOM reply.
- `dlm_slots_copy_in()` imports slot data from the low-node coordinator.
- `dlm_slots_assign()` assigns slots for all nodes when the local node is the low nodeid.

Slot assignment preserves existing slots, rejects slot changes after assignment, increments generation, logs the resulting map, and checks that the serialized slot list fits in `DLM_MAX_APP_BUFSIZE`.

## Membership Lists

Members are stored in `ls_nodes` ordered by nodeid, with removed members moved to `ls_nodes_gone`. `dlm_is_member()` and `dlm_is_removed()` query these lists.

`dlm_add_member()` allocates a member, starts/connects remote communication for nonlocal nodes, and inserts the member. `dlm_clear_members()` removes all active members and informs midcomms for remote nodes.

`make_member_array()` builds a weighted nodeid array for directory/master selection, treating all weights as one if every node has weight zero.

## Recovery Integration

`dlm_recover_members()` reconciles config-layer recovery membership input with DLM’s active lists:
- Counts previously removed members as negative recovery.
- Moves gone or re-added members to `ls_nodes_gone`.
- Calls midcomms removal and lockspace ops slot recovery for removed members.
- Adds new members.
- Updates `ls_low_nodeid`.
- Rebuilds the weighted member array.
- Pings all members with status RCOMs to establish communications.

## Lockspace Stop/Start

`dlm_ls_stop()` stops normal locking and receive processing for a recovery cycle. It sets recovery stop flags, clears running state, activates request queue blocking, waits until recovery owns `ls_in_recovery`, suspends recoverd, clears slot state, resumes recoverd, and calls optional `recover_prep`.

`dlm_ls_start()` reads current config nodes, creates a `dlm_recover` argument block with a new recovery sequence, stores it in the lockspace, and wakes recoverd.

## Important Behaviors and Invariants

- Membership changes must be reported to lockspace ops and midcomms before recovery may abort.
- Removed members stay in `ls_nodes_gone` until recovery completes so purging and remastering can recognize them.
- Userspace guarantees all nodes stop before any node starts the next recovery.
- `ls_recv_active`, `ls_recover_lock`, and `ls_requestqueue_lock` order the transition into recovery.

## Research Notes

Read completely. This file is the bridge between configfs/cluster membership and the recovery state machine.
