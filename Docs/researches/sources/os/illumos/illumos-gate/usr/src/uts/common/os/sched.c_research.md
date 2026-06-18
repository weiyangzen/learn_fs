# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sched.c

## Purpose

Implements the historical memory scheduler/swapper. It swaps LWPs and process address spaces in or out based on free-memory pressure, scheduling-class swap priorities, sleep time, and safe swap points.

## Main State

- `runout`, `runin`, `wake_sched`, and `wake_sched_sec` coordinate swapper sleep/wakeup.
- `tswap_queue` contains runnable threads that reached a safe point after being marked for swap.
- `avefree`, `avefree30`, `min_procsize`, `maxslp`, and system paging rates influence swap decisions.
- Counters track total swapins/swapouts and soft, hard, and swap-queue swapouts.

## Key Interfaces and Flow

- `sched()` is the main loop:
  - processes queued safe-point swapouts;
  - detects desperate memory conditions;
  - scans `practive` under `pidlock`;
  - chooses the best process to swap in by class-provided priority;
  - performs soft swaps of sleeping/deadwood processes when memory is below desired thresholds;
  - unloads modules and segkp cache under pressure;
  - chooses a hard-swap victim when needed;
  - blocks on `runout` or `runin` using CPR-safe callbacks when no work can proceed.
- `swapin()` faults swapped kernel stacks back into memory, sets `TS_LOAD`, decrements process swap counts, updates stats, and requeues runnable threads.
- `swapout()` marks or removes swappable threads, unlocks stack pages with `segkp_fault(... F_SOFTUNLOCK ...)`, increments process swap counts, and swaps out the address space when all LWPs are out.
- `swapout_lwp()` is called by an LWP reaching a safe point after `TS_SWAPENQ`; it moves itself to the swap queue and switches away.
- `process_swap_queue()` drains `tswap_queue`, unloads stacks, and swaps address spaces when all LWPs are swapped.

## Locking and Safety

- `pidlock` protects process-list traversal.
- `p_lock` stabilizes target process state while choosing and changing thread swap state.
- `thread_lock()`/dispatcher locks protect per-thread scheduling flags and queues.
- `swapped_lock` protects `tswap_queue` and threads whose dispatcher lock points there.
- The code carefully drops `p_lock` around stack faulting operations and reacquires it afterward.

## Dependencies

Uses scheduling-class callbacks `CL_SWAPIN`/`CL_SWAPOUT`, dispatcher queues, segkp stack backing, address-space swapout, module reclaim, CPR callbacks, DTrace scheduler probes, CPU VM stats, and process/thread state flags.

## Notes for Future Work

- The code is deeply tied to legacy swapping semantics and safe-point flags such as `TS_DONT_SWAP`, `TS_SWAPENQ`, `TS_ON_SWAPQ`, and `TS_LOAD`.
- Error from stack soft-unlock during swapout is treated as fatal panic.
