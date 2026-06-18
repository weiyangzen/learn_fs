# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_ipiq.c

## Scope

This file implements DragonFlyBSD's machine-independent LWKT IPI queue layer. It queues cross-CPU function calls, drains incoming IPI FIFOs, supports passive non-urgent IPIs, synchronizes CPUs through IPI-driven barriers, and exposes debug/statistics sysctls including latency probes.

## Public And Internal APIs Covered

- IPI send APIs: `lwkt_send_ipiq3()`, `lwkt_send_ipiq3_passive()`, `lwkt_send_ipiq3_bycpu()`, `lwkt_send_ipiq3_mask()`.
- Completion wait: `lwkt_wait_ipiq()`.
- IPI processing: `lwkt_process_ipiq()`, `lwkt_process_ipiq_frame()`, internal `lwkt_process_ipiq_nested()`, `lwkt_process_ipiq_core()`.
- Synchronization helpers: `lwkt_synchronize_ipiqs()`, `lwkt_cpusync_simple()`, `lwkt_cpusync_interlock()`, `lwkt_cpusync_deinterlock()`, `lwkt_cpusync_quick()`.
- Remote synchronization callbacks: `lwkt_cpusync_remote1()`, `lwkt_cpusync_remote2()`.
- Debug/sysctl support: aggregate `ipiq_*` statistics, optional panic-debug counters, and `debug.ipiq.latency_test` plus per-CPU latency logs.

## Control Flow And Behavior

- Each CPU owns a sender-to-target IPI FIFO for every possible target CPU. `lwkt_send_ipiq3()` appends a function/argument tuple to the sender's FIFO for the target CPU and sets the sender bit in the target's `gd_ipimask`.
- Local sends short-circuit by invoking the callback directly.
- Normal sends enter a critical section, raise `gd_intr_nesting_level`, and use store/load fences around FIFO publication and consumption.
- If a sender FIFO is too full, the sender enables physical interrupts and processes inbound IPIQs while waiting for the target to drain. This avoids APIC and cross-FIFO deadlocks when CPUs are mutually blocked sending IPIs.
- Nested senders use a higher FIFO threshold and a drain target so callbacks can queue more IPIs without exhausting the ring. `lwkt_process_ipiq_nested()` only processes queues whose senders requested draining.
- The actual hardware IPI is coalesced through `target->gd_npoll`; if another IPI is already pending or being processed, the sender avoids another hardware interrupt and increments `ipiq_avoided`.
- Passive sends enqueue without sending a hardware IPI until the queue reaches one-quarter full; these are intended for non-critical work such as deferred frees.
- `lwkt_wait_ipiq()` waits for a target to execute through a sequence number by repeatedly processing local IPIs and warning/panicking if progress stalls.
- `lwkt_process_ipiq()` and `_frame()` walk `gd_ipimask`, process each source CPU's FIFO for the current CPU, clear/re-set mask bits based on remaining work, then process the local `gd_cpusyncq`.
- `lwkt_process_ipiq_core()` snapshots `ip_windex`, uses a load fence, executes callbacks through that stable bound, advances `ip_rindex`, and updates `ip_xindex` only after the callback returns.
- CPU sync interlock sends stage-1 callbacks to target CPUs; remote CPUs acknowledge and requeue themselves on `gd_cpusyncq` until the master clears `cs_mack`, then execute the sync function and acknowledge stage 2.
- `lwkt_cpusync_quick()` skips the quiescent spin stage and only waits for remote execution acknowledgements.

## State And Data Structures

- Per-CPU `ipiq_stats_percpu` tracks sends, FIFO-full waits, avoided hardware IPIs, passive sends, and CPU sync counts.
- Per-CPU globaldata fields used here include `gd_ipiq[]`, `gd_ipimask`, `gd_npoll`, `gd_processing_ipiq`, `gd_intr_nesting_level`, `gd_cpusyncq`, `gd_other_cpus`, and thread `td_cscount`.
- FIFO state is tracked by `ip_windex`, `ip_rindex`, `ip_xindex`, `ip_drain`, and `ip_info[]` entries.
- CPU sync state uses `lwkt_cpusync` fields `cs_mask`, `cs_mack`, `cs_func`, and `cs_data`.

## Dependencies

- Depends on SMP CPU routing (`cpu_send_ipiq()`, `globaldata_find()`, cpumask operations), critical sections, atomic cpumask operations, CPU fences, TSC timing, and `tsleep`/`wakeup`.
- Used by LWKT scheduling, thread migration, message ports, and other cross-CPU kernel subsystems needing callback execution on a target CPU.

## Risks And Invariants

- FIFO index publication requires strict memory ordering: callback data must be visible before `ip_windex`, and callback completion must precede `ip_xindex`.
- The send path intentionally enables interrupts while waiting for FIFO space; doing otherwise can deadlock the IPI subsystem.
- `gd_processing_ipiq` prevents redundant hardware IPIs and informs nested drain behavior.
- CPU sync masters must avoid recursively reflagging cpusync work while `td_cscount` is non-zero, or synchronization can livelock.
- Callback functions run in hard/critical IPI context and must respect nesting, blocking, and reentrancy constraints.
