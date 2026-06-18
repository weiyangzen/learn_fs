# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_heartbeat.c

Read completely: 773 lines.

Implements `heartbeat(9)`, a periodic CPU progress monitor that detects stalled timecounter updates, stuck soft interrupts on the local CPU, and stopped progress on peer CPUs. It uses per-CPU heartbeat counters/cached uptimes, a low-priority clock softint, sysctl tuning, cross-calls, and IPIs to force useful panic traces.

Core state:
- `heartbeat_lock` serializes updates to `heartbeat_max_period_secs` and `heartbeat_max_period_ticks`.
- `heartbeat_sih` is the softint handle established by `heartbeat_start()`.
- Per-CPU fields include heartbeat count, cached uptime, stamp, and suspend nesting count.

Control and sysctl:
- `heartbeat_suspend()` increments the current CPU's suspend count for CPU offline transitions or polling-mode console input.
- `heartbeat_resume()` resets local heartbeat state at `splsched()` and decrements the suspend count.
- `heartbeat_resume_cpu()` resets count, uptime cache, and stamp for a CPU.
- `set_max_period()` validates overflow boundaries, resets all CPU heartbeat state when enabling from disabled state, and stores seconds/ticks values atomically.
- `heartbeat_max_period_sysctl()` implements `kern.heartbeat.max_period`, allowing runtime enable/disable and period changes with overflow checks.
- `sysctl_heartbeat_setup()` creates `kern.heartbeat` and its read/write `max_period` node.

Monitoring:
- `heartbeat_start()` establishes a low-priority MPSAFE clock softint and enables monitoring with `HEARTBEAT_MAX_PERIOD_DEFAULT`.
- `heartbeat_intr()` runs as a softint, stamps the local heartbeat count, and updates the local cached `time_uptime32`.
- `heartbeat()` is called from hard timer context with stable current CPU. It exits if disabled, locally suspended, or panicking; increments local heartbeat count; checks whether the timecounter has failed to advance for too many ticks; checks whether local softints are stuck by comparing `time_uptime32` to the softint-updated cache; schedules the softint; selects another online unsuspended CPU; and checks whether that CPU's cached uptime has advanced recently.
- `heartbeat_timecounter_suspended()` suppresses timecounter-stall panics when the primary CPU is suspended because the timecounter may not advance.
- `select_patient()` chooses the next online, unsuspended CPU after the current CPU in CPU iteration order, wrapping to the first candidate.

Failure handling:
- `defibrillate()` reports the stalled peer CPU, sends it an IPI, waits up to one second for acknowledgement, and panics locally if the peer cannot respond.
- `defibrillator()` acknowledges the IPI and panics on the stalled CPU to capture that CPU's stack, unless a panic is already in progress.
- With DDB, `heartbeat_dump()` prints per-CPU heartbeat fields safely through debugger byte reads.

Concurrency and invariants:
- Most fast-path reads/writes use relaxed atomics because heartbeat data is diagnostic/progress state.
- Enabling checks uses cross-calls so online CPUs reset local caches before the global period becomes nonzero.
- Arithmetic bounds keep uptime/tick deltas safely below 32-bit wrap concerns.

Risks and notes:
- Single-CPU systems cannot check another CPU and rely on local timecounter/softint checks.
- Some high-IPL single-CPU stalls need a hardware watchdog; the file's manual test notes call this out.
- `heartbeat_resume_cpu()` asserts current CPU stability except during cold startup.
