# File Research: sources/os/plan9/plan9/sys/src/9/teg2/clock.c

Cortex-A9 private timer and Plan 9 timekeeping implementation for the Tegra 2 port.

Key responsibilities:
- Uses Cortex local private timers for periodic clock interrupts and the Tegra 1 MHz counter for fast ticks.
- Defines local timer/watchdog and private global timer register layouts.
- Handles clock interrupts, calls `timerintr`, services Tegra watchdog state, and checks that other CPUs' clocks are still advancing.
- Initializes cycle counters/performance counters for user access.
- Calibrates delay-loop estimates and optional instruction-per-second diagnostics.
- Starts CPU-local watchdog support when enabled by compile-time conditionals.
- Implements `clockshutdown`, `clockinit`, `timerset`, `fastticks`, `lcycles`, `microdelay`, and `delay`.

Important behavior:
- `fastticks` extends the 32-bit 1 MHz counter into `m->fastclock` by detecting low-word wrap under `splhi`.
- `timerset` converts desired fasttick offset into private-timer cycles, clamping between minimum and maximum periods.
- Secondary CPU local timers are unmasked rather than registered through normal IRQ setup.
- `clockprod` can prod a stuck secondary CPU by forcing timer handling and resetting its local timer.

Dependencies and assumptions:
- Assumes the private local timer rate is `250 MHz / 2`, per source comment.
- Depends on Tegra shared clock functions, GIC helpers, CP15 performance counter access, and Plan 9 timer infrastructure.

Notable risks:
- Several watchdog paths are compiled out under `watchdog_not_bloody_useless`.
- Multiprocessor clock sanity can panic if another CPU's tick count diverges by more than one second after startup.
