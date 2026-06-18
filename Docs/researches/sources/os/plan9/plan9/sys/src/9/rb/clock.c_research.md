# File Research: sources/os/plan9/plan9/sys/src/9/rb/clock.c

Atheros AR7161/RouterBOARD RB450G MIPS clock, watchdog, delay, and fast-tick support.

Key responsibilities:
- Controls watchdog timer: silence, reset-on-timeout, immediate reset, stop, and shutdown.
- Implements millisecond and microsecond delays using CP0 count.
- Handles clock interrupts by programming CP0 compare, petting watchdog, and calling `timerintr`.
- Calibrates approximate MIPS rate with an instruction loop.
- Initializes per-Mach timing fields, compare interrupt period, and enables clock interrupt level.
- Implements `timerset`, `fastticks`, `µs`, `perfticks`, `lcycles`, `cycles`, and `syncclock`.

Important behavior:
- Assumes RB450G base tick frequency of 680 MHz divided by MIPS 24K count divisor 2.
- `microdelay` resets CP0 count if target wraps or is too close to `~0`.
- `fastticks` rewrites compare if the next interrupt is too far away to avoid lost interrupts.
- Multiprocessor sync support exists but `conf.nmach` is effectively one for this board.

Dependencies:
- Depends on CP0 assembly helpers, AR7161 reset/watchdog registers from `io.h`, and Plan 9 timer infrastructure.

Notable risks:
- Frequency is hard-coded for RB450G.
- Delay and fasttick code mutate CP0 count/compare under `splhi`, which affects timing assumptions.
