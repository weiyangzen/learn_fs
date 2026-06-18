# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock.c

This file implements the main illumos kernel clock service: the periodic `clock()` cyclic, NTP/PPS discipline state, wall-clock/TOD synchronization, process tick handling, delay routines, deadman timers, load-average maintenance, and the hybrid `lbolt` implementation.

Core behavior:
- `clock()` runs from `clock_cyclic` every `nsec_per_tick`, skips work during panic, refreshes `freemem`, applies precision-kernel phase adjustments to `timedelta`, samples CPU/partition runnable state, updates lgroup load, schedules per-thread tick accounting via `clock_tick_schedule()`, invokes cluster/cpucap clock callouts, and performs once-per-second VM/system accounting.
- Once-per-second logic handles NTP leap states, `time_maxerror`, PLL/FLL phase/frequency adjustment, PPS watchdog expiry, TOD drift comparison, `hrestime` correction, TOD chip resync, `lbolt_cv` broadcast, swap and run queue accounting, `fsflush` wakeup, `vmmeter()`, load averages, and swapper wakeups.
- `clock_update()` is called under `tod_lock` by `ntp_adjtime()` to update `time_offset`, `time_freq`, and `time_reftime`, and marks the TOD for later sync.
- `ddi_hardpps()` handles external PPS interrupts with median filters for phase and frequency, jitter/wander/error accounting, adaptive calibration interval selection, and PPS-driven `pps_freq` updates.
- `clock_tick()` charges a target LWP/process for pending ticks: scheduler class ticks, user/system tick counters, profiling ASTs, virtual/prof interval timers, process/task CPU-time resource controls, and RSS usage.
- `profil_tick()` drains `lwp_oweupc` and updates old-style profiling counters or PC-sampling buffers in user memory.
- `delay()`, `delay_random()`, and `delay_sig()` implement tick-based sleeps using callouts/CVs when timeouts are available, with spin fallback during panic or devinfo freeze.
- `clkset()` initializes system time from TOD or an approximate filesystem time; `set_hrestime()` resets `hrestime`, clears `timedelta`, increments `timechanged`, and calls callout users.
- `deadman_init()` installs per-CPU high-level cyclics that detect clock inactivity and panic if enabled; during panic the same path can time out crash dumps.
- `tod_fault()`, `tod_status_set()`, `tod_status_clear()`, `tod_set_prev()`, and `tod_validate()` implement TOD health tracking for reversed, stalled, jumped, rate-changed, and read-only TOD states.
- `clock_init()` registers the clock cyclic and lbolt cyclic and allocates cache-aligned per-CPU/global lbolt state.
- `lbolt_event_driven()`, `lbolt_ev_to_cyclic()`, `lbolt_cyclic_driven()`, and `lbolt_cyclic()` switch DDI lbolt reads between computed `gethrtime()/nsec_per_tick` mode and a cyclic-maintained counter under high call pressure.
- `lbolt_debug_entry()` and `lbolt_debug_return()` subtract debugger stop time from lbolt-visible uptime.

Important invariants:
- `tod_lock` protects TOD-facing clock update and validation state; `hr_clock_lock()` protects `hrestime`, `timedelta`, `tod_needsync`, and `timechanged` mutations.
- `clock_tick()` requires the process `p_lock` to be held and assumes a valid LWP.
- Delay callout/CV paths use the current thread’s `t_delay_lock` and `t_delay_cv`; interrupt-context use is diagnosable because `delay(9F)` is not valid there.
- `tod_validate()` is disabled until high-resolution time is usable and does not run after a TOD fault until reset.
- `lbolt_hybrid` mode switches are serialized with `lbi_token`; cyclic reprogramming is deferred to a softint for event-to-cyclic transitions.
- `lbi_debug_time` is subtracted from returned lbolt values so hardware reboot and debugger time do not leak into DDI lbolt semantics.
