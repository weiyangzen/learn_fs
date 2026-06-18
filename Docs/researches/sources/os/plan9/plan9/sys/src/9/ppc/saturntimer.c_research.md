# File Research: sources/os/plan9/plan9/sys/src/9/ppc/saturntimer.c

Saturn board timer support for Plan 9 PPC.

Key responsibilities:
- Defines Saturn timer register addresses and control bits.
- Implements microsecond conversion via cycle counter and cached multiplier.
- Handles timer interrupts, clearing timer events, acknowledging interrupt controller state, and calling `timerintr`.
- Initializes timer0 as the periodic/kernel event timer and timer1 as the free-running fast tick source.
- Implements `fastticks` using timer1 plus a software seconds counter.
- Implements `timerset` by programming timer0 with clamped offset.

Important behavior:
- Timer1 events increment a `ticks` counter and are also handled opportunistically in `fastticks`.
- `timerset` temporarily leaves only timer1 enabled while computing/reprogramming timer0.
- `timer_ctl` is cached and rewritten with event-clear bits.

Dependencies:
- Depends on `msaturn.h`, `m->bushz`, interrupt enablement, and PPC `cycles`.

Notable risks:
- Direct MMIO access uses raw casts to Saturn addresses.
- `fastticks` asserts timer1 is enabled and mutates timer control state.
