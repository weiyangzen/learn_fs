# File Research: sources/os/plan9/plan9/sys/src/9/teg2/clock-tegra.c

Tegra 2 shared timer and 1 MHz microsecond-counter support, excluding Cortex private timers.

Key responsibilities:
- Defines Tegra shared countdown timer and microsecond counter register layouts.
- Services and clears the Tegra watchdog/shared timer interrupt.
- Starts the Tegra shared watchdog timer on CPU0 with `tegclock0init`.
- Shuts down the shared watchdog/timer from CPU0.
- Verifies the 1 MHz counter is configured by U-Boot as expected and is ticking.
- Provides `perfticks()` from the free-running microsecond counter.

Important behavior:
- `tegclockintr` reads timer trigger to appease the watchdog.
- The watchdog period is halved because the Tegra watchdog fires on the second missed interrupt.
- `perfticks` never returns zero, preventing `m->fastclock` from becoming zero.

Dependencies and assumptions:
- Assumes U-Boot left `soc.microsecond-counter cfg` as `0xb` for a 12 MHz peripheral clock divisor.
- Depends on `soc.tmr`, `soc.µs`, `irqenable`, and clock/watchdog constants.

Notable risks:
- The shared timer/watchdog behavior is tied to sparse documentation, including the required trigger read.
