# File Research: sources/os/linux/linux/mm/oom_kill.c

## Role

Linux out-of-memory killer implementation. It chooses victims when reclaim cannot satisfy allocations, handles global and memory-cgroup OOMs, coordinates OOM victim state and memory reserves, logs diagnostic state, optionally panics, runs the MMU OOM reaper, exposes OOM notifier registration, and implements `process_mrelease`.

## Key Behavior

- Defines sysctls for `panic_on_oom`, `oom_kill_allocating_task`, and `oom_dump_tasks`; `oom_init()` starts the `oom_reaper` thread on MMU builds and registers the sysctls.
- `oom_lock` serializes OOM killer invocations and coordinates with `oom_killer_disable()`. `oom_adj_mutex` serializes updates to score-adjust state elsewhere.
- `oom_cpuset_eligible()` limits candidate victims for NUMA/cpuset/mempolicy-constrained OOMs. It checks mempolicy node intersection when a nodemask constrains the allocation, otherwise cpuset memory intersection with the triggering task.
- `find_lock_task_mm()` finds a thread in a process group that still has a live `mm` and returns it with `task_lock()` held, handling exiting group leaders and `kthread_use_mm()` cases.
- `oom_badness()` implements victim scoring from RSS, swap entries, and page-table memory, adjusted by `oom_score_adj`. It excludes init, kernel threads, unkillable tasks, already skipped/reaped mms, and vfork participants.
- `constrained_alloc()` classifies OOM scope as unconstrained, cpuset-constrained, memory-policy-constrained, or memcg. It also sets `oc->totalpages` for score normalization.
- `select_bad_process()` scans either memcg member tasks or all system processes with `oom_evaluate_task()`, keeping the eligible task with the highest badness score. It aborts selection if a prior OOM victim likely still needs time to release memory.
- Diagnostic helpers print task tables, OOM context, memcg context, system memory state, unreclaimable slab when relevant, and victim summaries. Dumps are rate-limited in the kill path.
- `mark_oom_victim()` sets `TIF_MEMDIE`, records `signal->oom_mm`, increments the global victim count, thaws frozen victims, and emits tracing. `exit_oom_victim()` clears the flag and wakes waiters when the last victim exits.
- `oom_killer_disable()` prevents new OOM kills, then waits for all in-flight victims to exit or times out and re-enables the killer.
- `task_will_free_mem()` detects whether a task or all processes sharing its `mm` are already exiting and likely to free memory without selecting an additional victim.
- On MMU builds, the OOM reaper asynchronously tries to reclaim anonymous/private memory from killed tasks. It waits for a delayed timer, takes `mmap_read_trylock()`, skips mms already marked `MMF_OOM_SKIP`, calls `zap_vma_for_reaping()` on reapable VMAs, logs results, retries briefly, and then marks the mm skipped.
- `__oom_kill_process()` normalizes the victim to a thread with an `mm`, sends SIGKILL before granting memory reserves, marks the victim, logs memory footprint, kills other user processes sharing the same `mm`, avoids reaping when global init pins the mm, and queues the reaper when safe.
- `oom_kill_process()` first handles already-dying victims by granting reserves and queuing reaping. Otherwise it logs diagnostics, optionally resolves a memcg OOM group, kills the selected victim, and kills all eligible tasks in the chosen OOM group.
- `check_panic_on_oom()` honors `panic_on_oom`: value 1 only panics for unconstrained global OOM; value 2 panics for all non-sysrq OOMs.
- `out_of_memory()` is the top-level OOM entry. It refuses when disabled, invokes registered notifiers for global OOM, grants reserves to current if it is already dying, skips global kills for non-`__GFP_FS` IO-less reclaim contexts, classifies constraints, handles panic policy, optionally kills the allocating task, selects a bad process, and panics if a real global OOM has no killable process.
- `pagefault_out_of_memory()` handles leaked `VM_FAULT_OOM` from page faults by synchronizing memcg OOMs and logging a rate-limited warning for global retry cases.
- `process_mrelease(pidfd, flags)` lets userspace ask the kernel to reclaim memory from a process that is already exiting or OOM-skipped. It validates flags, resolves the pidfd, finds a live `mm`, checks `task_will_free_mem()`, and calls `__oom_reap_task_mm()` under the mmap read lock on MMU builds.

## Dependencies

Uses scheduler/task iteration, memcg APIs, cpusets, NUMA mempolicy, notifier chains, sysctl, freezer, credentials, tracepoints, mmap and VMA internals, MMU notifier/reaping helpers, pidfd task lookup, signal delivery, VM counters, slab diagnostics, and page allocator OOM control structures.

## Research Notes

The file's main invariant is that only one OOM decision path proceeds at a time, while victims are marked quickly enough to access reserves and make progress toward exit. The OOM reaper is intentionally conservative: it avoids blocking locks and only targets memory that can be discarded without filesystem or device coordination. The highest-risk logic is in candidate eligibility and shared-`mm` handling, because killing or reaping the wrong task can either fail to free memory or disrupt protected/system-critical processes.
