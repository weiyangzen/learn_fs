# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_tc.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_tc.c`.
- Subset scope: `Docs/research_subset_a.md`, which includes `sources/os/bsd/netbsd-src`.
- This file implements NetBSD's kernel timecounter framework, lockless time read paths, boot/realtime base handling, timecounter registration/detach, UTC stepping, NTP second windup, and RFC 2783 PPS support.

## Purpose And Main Interfaces

- Provides early dummy timecounter support until real hardware timecounters are registered.
- Maintains a ring of `struct timehands` snapshots used by readers without taking `timecounter_lock`.
- Exports high-resolution time APIs:
  - `binuptime`, `nanouptime`, `microuptime`
  - `bintime`, `nanotime`, `microtime`
  - cached `get*` variants such as `getnanotime`, `getmicrotime`, `getbinboottime`
- Exports timecounter lifecycle:
  - `tc_init`
  - `tc_detach`
  - `tc_gonebad`
  - `tc_getfrequency`
  - `inittimecounter`
  - `tc_ticktock`
- Exports time setting:
  - `tc_setclock`
- Implements PPS APIs:
  - `pps_ioctl`
  - `pps_init`
  - `pps_capture`
  - `pps_event`
  - `pps_ref_event`

## Key Data Structures

- `struct timehands` contains the active timecounter pointer, counter-to-time scale, counter offset, bintime offset, cached micro/nano realtime, and a generation counter.
- `timehands` is a volatile pointer to the current published timehands snapshot.
- `timecounter` is the currently selected hardware counter.
- `timecounters` is the registered counter list.
- `timebase` is a seqlock-like structure storing boot-time offset used to convert uptime to realtime.
- `time__second` / `time__uptime` or 32-bit fallback storage provide fast global second snapshots.

## Control Flow

- `tc_init` validates counter frequency relative to `hz`, inserts it into the counter list, and may auto-select it when quality/frequency is better than the current counter.
- `tc_windup` copies the current timehands into the next ring slot, applies hardware counter deltas, handles NTP second updates, caches realtime values, recalculates scaling, publishes the new generation, and advances `timehands`.
- Readers loop on `th_generation` to avoid torn reads while `tc_windup` updates a slot.
- `tc_detach` removes a counter, switches away if necessary, bumps a removal generation, and waits until all LWPs have stopped referencing old counter state.
- `tc_setclock` changes UTC by updating `timebase`, then winds up timehands and optionally logs the step.
- `tc_ticktock` periodically calls `tc_windup` and switches counters if a selected counter was marked bad.
- PPS handling captures counter values, converts them to timestamps against the captured timehands, handles reference modes, applies offsets, updates sequences, and optionally feeds `hardpps`.

## Concurrency And Invariants

- `timecounter_lock` serializes counter list changes and windup.
- Lockless readers use generation checks and memory barriers.
- Timecounter detach safety uses per-LWP `l_tcgen`, `timecounter_removals`, and `xc_barrier`.
- `timebase.gen` is odd while changing and even while stable.
- 32-bit architectures emulate atomic 64-bit time snapshots with sentinel high words and producer/consumer barriers.

## Risks And Edge Cases

- Any incorrect generation/barrier change can create torn or non-monotonic time reads.
- `tc_detach` must not free a counter until all readers have left old generations.
- Large time steps are capped for NTP update looping by `LARGE_STEP`.
- PPS paths depend on stable captured timehands; events are dropped if windup or counter changes invalidate captured state.
- Low-quality or insufficient-frequency counters are demoted to avoid overflow between hardclock updates.
