# File Research: sources/os/linux/linux-stable/fs/dlm/recoverd.c

## Purpose
`recoverd.c` implements the per-lockspace recovery kernel thread and orchestrates the full DLM recovery sequence.

## Recovery Flow
`ls_recover()` performs:
1. Suspend callbacks.
2. Clear inactive RSBs.
3. Snapshot active RSBs into a root list.
4. Reconcile membership.
5. Recompute directory node ids.
6. Snapshot locally mastered RSBs for directory rebuild.
7. Set and wait for node recovery status.
8. Rebuild directory from peer master-name dumps.
9. Mark outstanding waiters before recovery.
10. If negative membership change or no-directory mode: purge, recover masters, recover locks, wait for lock barrier, recover RSB state.
11. Release root list.
12. Purge invalid queued directory requests.
13. Set/wait done barrier.
14. Clear removed-member list.
15. Resume callbacks.
16. Re-enable locking.
17. Process queued normal messages.
18. Recover waiters post-recovery.
19. Grant pending locks.

## Root and Master Lists
`dlm_create_root_list()` snapshots all active RSBs and holds references. `dlm_create_masters_list()` snapshots RSBs mastered locally for directory-name transfer during recovery.

Both lists are explicitly released after use.

## Locking Re-enable
`enable_locking()` only re-enables if the recovery sequence still matches. It sets `LSFL_RUNNING`, resumes the scan timer, releases `ls_in_recovery`, and clears `LSFL_RECOVER_LOCK`.

It holds `ls_recv_active` to avoid races with receive threads adding messages to the request queue while recoverd drains it.

## Recoverd Thread
`dlm_recoverd()` owns `ls_in_recovery` during stopped periods and wakes on:
- `LSFL_RECOVER_DOWN`
- `LSFL_RECOVER_WORK`
- kthread stop

`do_ls_recovery()` consumes `ls_recover_args`, clears `LSFL_RECOVER_STOP` only if the sequence still matches, records success or critical errors, completes `ls_recovery_done`, and calls lockspace `recover_done` ops on success.

## Risks and Notes
Recovery is intentionally non-abortable until membership changes have been reported to lockspace ops and midcomms. Later phases abort on `-EINTR` and wait for a newer recovery cycle.
