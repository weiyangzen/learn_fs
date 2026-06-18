# File Research: sources/os/linux/linux-stable/fs/dlm/recover.c

## Purpose
`recover.c` implements core DLM recovery helpers: recovery barriers, master remapping, lock-copy replay, LVB recovery, conversion repair, inactive RSB cleanup, and recovery-status coordination.

## Wait and Barrier Helpers
`dlm_wait_function()` waits for a condition or recovery stop, with periodic timeout checks and `LSFL_RCOM_WAIT` timeout handling.

Recovery barrier helpers use the low-node protocol:
- Low node polls all members for a status.
- Non-low nodes poll the low node for the `_ALL` status bit.
- Status stages include nodes, directory, locks, and done.

`dlm_recover_members_wait()` also coordinates slot assignment/copying.

## Recovery Tracking Structures
Two mechanisms track outstanding recovery work:
- `ls_recover_list` for RSBs waiting on recovered lock replies.
- `ls_recover_xa` for RSBs waiting on async master lookup replies, keyed by temporary ids.

Both hold RSB references while work is pending and clear state on errors.

## Master Recovery
`dlm_recover_masters()` walks the recovery root list. For RSBs mastered by removed nodes, it either:
- assigns static masters in no-directory mode, or
- sends async RCOM lookup requests to directory nodes.

Replies are handled by `dlm_recover_master_reply()`, which updates `res_master_nodeid`, `res_nodeid`, and marks RSBs as new masters.

## Lock Recovery
`dlm_recover_locks()` sends local process-copy locks for remastered RSBs to their new masters. It counts outgoing locks per RSB and waits until all replies are processed.

`dlm_recovered_lock()` decrements the per-RSB count, clears `RSB_NEW_MASTER`, removes the RSB from the recover list, and wakes the general waitqueue when complete.

## RSB Finalization
`dlm_recover_rsbs()` finalizes master RSB state:
- fixes incompatible PR/CW conversion recovery with `recover_conversion()`
- recovers or invalidates lock value blocks with `recover_lvb()`
- marks resources needing grant processing with `recover_grant()`
- clears recovery flags

`recover_lvb()` chooses LVB content from the strongest granted/converting lock with LVB data, or the highest LVB sequence among NL/CR locks, and sets `RSB_VALNOTVALID` where appropriate.

## Inactive Cleanup
`dlm_clear_inactive()` removes all inactive/tossed RSBs from the hash table and scan lists before recovery rebuilds current state.

## Risks and Notes
The file is highly recovery-order dependent. The comments explain why all MSTCPY locks are purged/rebuilt even when a master remains the same: aborted recoveries can otherwise make waiters unable to distinguish valid replies from stale replies.
