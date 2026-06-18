# File Research: sources/os/plan9/9front/sys/src/9/kw/clock.c

Implements Kirkwood timer, clock interrupt, watchdog, and delay support.

Key elements:
- Defines Kirkwood timer registers and control bits.
- Clock interrupt reloads the watchdog, increments a sanity counter, calls `timerintr`, and clears the bridge interrupt.
- `clockinit` verifies timer interrupts, configures periodic timer0, free-running timer1, and watchdog reset output.
- `timerset` programs timer0 for next deadline within min/max bounds.
- `fastticks` extends the 32-bit timer into a monotonic 64-bit counter.
- Provides `perfticks`, `lcycles`, `µs`, `microdelay`, and `delay`.

Dependencies:
- Uses `soc.clock`, `soc.cpu`, interrupt bridge routines, and machine timing fields.

Research notes:
- Timer1 counts down; `perfticks` returns its bitwise complement as an increasing counter.
- `clockshutdown` also disables the watchdog.
