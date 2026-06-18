# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_rmlock.c

Read completely: 1258 lines.

## Purpose
Implements machine-independent read-mostly locks: classic `rmlock` with per-CPU reader trackers and backing writer lock, plus sleepable read-mostly `rmslock`.

## Main Elements
- Registers lock classes `lock_class_rm` and `lock_class_rm_sleepable`, including generic lock/unlock/assert/owner hooks and optional DDB display support.
- Represents read ownership with caller-supplied `struct rm_priotracker` entries on per-CPU `pc_rm_queue` lists, allowing fast local reader acquisition without taking the writer lock in the common case.
- Uses `rm_writecpus` as a CPU token bitmap. Writers restore tokens for CPUs that have readers by rendezvous/IPI cleanup and gather active readers into `rm_activeReaders`.
- `_rm_rlock()` installs a tracker, pins the scheduler, and usually completes as a fast path; `_rm_rlock_hard()` handles missing CPU tokens, recursive read ownership, trylock failure, and backing writer-lock acquisition.
- `_rm_runlock()` removes the tracker, unpins the scheduler, and `_rm_unlock_hard()` wakes a waiting writer when a signaled active reader exits.
- `_rm_wlock()` takes the backing mutex or sx lock, gathers all outstanding readers, marks active readers for signaling, and waits on the rmlock turnstile until all active readers drain.
- `_rm_wunlock()` releases the backing writer primitive.
- Debug wrappers integrate with WITNESS, lock logging, lock counters, idle-thread checks, destroyed-lock detection, and recursion assertions.
- `_rm_assert()` can compute exact read recursion count for the current thread by walking the current CPU's tracker list.
- DDB support prints write CPU bitmap, per-CPU readers, active readers, and backing write-lock state.
- The second half implements `rmslock`, a sleepable read-mostly primitive with per-CPU reader counters, an `influx` flag for IPI synchronization, a mutex-serialized writer side, and no reader/writer priority propagation.
- `rms_rlock()`/`rms_runlock()` use per-CPU counters in the writer-free fast path; writer presence routes through fallback paths using the global mutex and sleep/wakeup.
- `rms_wlock()` switches all per-CPU reader counts into a global count using `smp_rendezvous_cpus_retry()`, waits for readers, serializes concurrent writers with transient ownership, and records the owning thread.

## Dependencies And Integration
Depends on per-CPU data, scheduler pinning, critical sections, SMP rendezvous/IPI mechanisms, turnstiles, WITNESS, lock profiling/logging, DDB, mutexes, sx locks, and UMA per-CPU allocation for `rmslock`.

## Risk Notes
The fast paths rely on strict interrupt fences, critical-section nesting, and per-CPU queue consistency during local interrupt traversal. Writers depend on correctly transferring readers from per-CPU lists/counters to global wait state. `rmslock` intentionally has no priority propagation and is suitable only for very rare writes.
