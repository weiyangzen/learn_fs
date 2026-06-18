# File Research: sources/os/linux/linux/fs/dlm/recover.c

## Role

`recover.c` implements the internal DLM recovery algorithms for waiting on recovery barriers, recovering resource masters, rebuilding lock copies, and finalizing resource state after membership changes.

## Barrier Waiting

`dlm_wait_function()` waits for a condition or recovery stop, with periodic timeout checks for synchronous RCOM waits.

Recovery status uses a low-node coordination pattern:
- the lowest node polls every member for a status bit
- once all have it, the low node sets the corresponding `_ALL` bit
- other nodes poll the low node for `_ALL`

This is used for members, directory, locks, and done stages.

## Member Slot Recovery

`dlm_recover_members_wait()` initializes member slots, waits for all nodes to reach the node stage, and either assigns slots as the low node or imports slots from the low node.

## Master Recovery

For resources whose master departed, `dlm_recover_masters()` walks active root resources and either:
- computes a static new master when no directory is used, or
- sends async lookup RCOMs to directory nodes.

Outstanding master lookups are tracked in `ls_recover_xa` with local resource ids. `dlm_recover_master_reply()` updates the resource master and removes the lookup from the xarray.

`set_new_master()` updates lock nodeids and marks resources for later lock and LVB recovery.

## Lock Recovery

`dlm_recover_locks()` sends every local grant/convert/wait LKB on remastered resources to the new master. Outstanding resource lock-copy operations are tracked on `ls_recover_list`.

`dlm_recovered_lock()` decrements the per-resource recovery count, clears `RSB_NEW_MASTER` when done, and wakes recovery when all copies are complete.

## LVB and Grant Finalization

`recover_lvb()` determines the recovered resource LVB and `RSB_VALNOTVALID` state:
- invalidates when a master lost an EX/PW lock from a failed node
- for new masters, chooses an LVB from the strongest lock above CR, or the highest LVB sequence among NL/CR locks
- invalidates if only NL/CR LVB locks remain

`recover_conversion()` handles PR/CW conversion conflicts by dropping incompatible granted conversion mode to NL so recovery grant can re-evaluate.

`recover_grant()` marks new masters with waiting/converting locks for recovery grant processing.

`dlm_recover_rsbs()` runs these finalization steps for all mastered resources and clears recovery flags.

## Inactive Cleanup

`dlm_clear_inactive()` removes and frees slow-inactive RSBs from the rhashtable before recovery proceeds.

## Important Behaviors and Invariants

- Recovery list and xarray counts must return to zero; error paths clear outstanding state.
- Resource locks are held while modifying master and queue state.
- All MSTCPY locks are purged/rebuilt even if a master remains effectively the same, because aborted recovery can make request replies ambiguous.
- LVB recovery must occur before recovery grant so completions present the correct LVB state.

## Research Notes

Read completely. This file contains the main data-structure recovery logic, while `recoverd.c` sequences it.
