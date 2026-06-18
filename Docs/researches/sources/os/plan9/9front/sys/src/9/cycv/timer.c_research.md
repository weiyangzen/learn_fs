# File Research: sources/os/plan9/9front/sys/src/9/cycv/timer.c

Role: Cyclone V timer and delay support using MPCore global/local timers and clock-manager PLL values.

Key responsibilities:
- Implements `microdelay()`, `delay()`, `µs()`, and `fastticks()` over the global timer registers.
- Reads a stable 64-bit global timer value by sampling high/low/high.
- Programs the local timer compare interval in `timerset()` with range clamping.
- Handles local timer interrupts in `timerirq()` and delegates to `timerintr()`.
- Initializes CPU frequency from clock-manager VCO fields and enables global/local timers.
- Registers `TIMERIRQ` as the clock interrupt.

Dependencies:
- Uses `CLOCKMGR_BASE`, `mpcore`, `HPS_CLK`, timer IRQ constants, and Plan 9 timer core callbacks.
- `synccycles()` is intentionally empty on this platform.

Notes:
- `timerhz` is set to `m->cpuhz / 4`, matching global timer control divider setup.
