# File Research: sources/os/linux/linux/fs/dlm/recoverd.c

## Role

`recoverd.c` implements the per-lockspace recovery kernel thread and the top-level recovery sequence.

## Recovery Lists

`dlm_create_root_list()` snapshots all active RSBs for recovery work. `dlm_create_masters_list()` snapshots active local-master RSBs for directory rebuild. Both hold references and have matching release helpers.

## Recovery Sequence

`ls_recover()` performs the staged recovery:
1. suspend callbacks
2. clear inactive RSBs
3. snapshot root RSBs
4. reconcile membership
5. recompute directory nodeids
6. snapshot local masters
7. mark node stage and wait for all members
8. rebuild the directory from peer master-name data
9. mark/wait directory stage
10. recover waiters before remastering
11. if nodes departed or no directory exists, purge departed locks, recover masters, recover locks, wait lock stage, and recover RSB state
12. otherwise still participate in the lock-stage barrier
13. purge stale requestqueue entries
14. mark/wait done stage
15. clear gone members
16. resume callbacks
17. re-enable locking
18. process saved requestqueue
19. recover waiters post-recovery
20. grant recoverable locks

## Locking Re-enable

`enable_locking()` only re-enables locking if the recovery sequence has not been superseded. It resumes scan timers, releases `ls_in_recovery`, clears `LSFL_RECOVER_LOCK`, and synchronizes against receive paths with `ls_recv_active`.

## Recovery Thread

`dlm_recoverd()` starts with `ls_in_recovery` held and `LSFL_RECOVER_LOCK` set. It sleeps until `LSFL_RECOVER_DOWN` or `LSFL_RECOVER_WORK` is set. DOWN reacquires recovery exclusion; WORK runs `do_ls_recovery()`.

`do_ls_recovery()` consumes `ls_recover_args`, clears stop state if current, runs recovery, completes `ls_recovery_done` on success or fatal error, and leaves interrupted recovery to be queued again.

## Important Behaviors and Invariants

- Recovery may not abort until membership changes are reported to lsops and midcomms.
- Normal locking is enabled before saved requestqueue processing.
- Requestqueue purge happens after directory rebuild because old directory requests are invalid.
- `ls_recoverd_active` lets stop/start paths suspend the daemon at safe points.

## Research Notes

Read completely. This is the orchestration layer for the recovery protocol implemented across member, rcom, recover, dir, and lock code.
