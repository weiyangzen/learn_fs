# File Research: sources/os/linux/linux-stable/fs/dlm/member.c

## Purpose
`member.c` manages DLM lockspace membership across recovery cycles. It tracks current members, removed members, slot assignments, node weights, low-node coordination, and midcomms membership notifications.

## Slot Handling
Slot helpers support recovery-time slot negotiation:
- `dlm_slots_version()` checks whether a peer supports slot fields.
- `dlm_slot_save()` records a member slot/generation from RCOM status replies.
- `dlm_slots_copy_out()` serializes local slots into an RCOM reply.
- `dlm_slots_copy_in()` imports the low-node slot map.
- `dlm_slots_assign()` assigns stable slots when the local node is the low nodeid.

Slot assignment preserves prior slots, rejects unexpected slot changes, increments generation, logs slot maps, and verifies the serialized slot list fits in `DLM_MAX_APP_BUFSIZE`.

## Membership Lists
Active members are stored in `ls_nodes`, ordered by nodeid. Removed members are moved to `ls_nodes_gone` until recovery finishes.

Important helpers:
- `dlm_is_member()`
- `dlm_is_removed()`
- `dlm_clear_members()`
- `dlm_clear_members_gone()`

`dlm_add_member()` allocates a `struct dlm_member`, starts remote communication for nonlocal nodes, records weight/comm sequence, and inserts it.

## Weighted Directory Mapping
`make_member_array()` creates `ls_node_array` using configured member weights. If all weights are zero, each member is treated as weight 1. This array feeds directory/master hash placement.

## Recovery Integration
`dlm_recover_members()` reconciles config-layer recovery input with current state:
- Counts prior removed nodes as negative recovery.
- Moves departed or re-added members to `ls_nodes_gone`.
- Notifies midcomms and lockspace ops for removals.
- Adds new members.
- Recomputes `ls_low_nodeid`.
- Rebuilds the weighted node array.
- Pings members with status RCOMs to establish communication.

## Lockspace Stop/Start
`dlm_ls_stop()` blocks normal receive/message processing, sets recovery stop flags, clears running state, activates request queue blocking, waits for recovery ownership, suspends/resumes recoverd, clears slot state, and calls optional `recover_prep`.

`dlm_ls_start()` reads config nodes, creates a new `struct dlm_recover` with a fresh sequence, stores it as `ls_recover_args`, and wakes recoverd.

## Risks and Notes
Membership change reporting must not abort early because lockspace ops and midcomms must observe every add/remove. `ls_recv_active`, `ls_recover_lock`, and `ls_requestqueue_lock` are central to avoiding receive/recovery races.
