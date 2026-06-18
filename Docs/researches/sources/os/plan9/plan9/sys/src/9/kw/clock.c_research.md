# File Research: sources/os/plan9/plan9/sys/src/9/kw/clock.c

## Purpose
Implements Kirkwood timer, watchdog, delay, and fast tick support.

## Main Data Structures
- `TimerReg`: memory-mapped timer control, reload, current timer, watchdog reload, and watchdog counter registers.

## Behavior
- `clockshutdown` disables all timers and watchdog.
- `clockinit` verifies timer interrupt delivery, configures timer0 as the periodic kernel tick, timer1 as a free-running cycle/performance counter, and enables watchdog reset output.
- `clockintr` refreshes the watchdog, increments a local sanity tick counter, calls generic `timerintr`, and clears the CPU timer interrupt.
- `timerset` programs timer0 for the next deadline, clamped between `MinPeriod` and `MaxPeriod`.
- `fastticks` combines the 32-bit down/up performance tick source with `m->fastclock` high bits to produce a monotonic 64-bit value.
- `perfticks`, `lcycles`, and `µs` expose performance/cycle time.
- `microdelay` and `delay` busy-wait from `m->delayloop`.

## Dependencies and Integration
Uses `soc.clock`, `soc.cpu`, interrupt setup/clear helpers, generic timer interrupt code, CPU frequency constants, watchdog reset bits, and per-Mach time state.

## Risks and Notes
Timer0 sanity checking briefly lowers interrupt priority during initialization. Delay calibration starts from a fixed estimate until later adjustment.
