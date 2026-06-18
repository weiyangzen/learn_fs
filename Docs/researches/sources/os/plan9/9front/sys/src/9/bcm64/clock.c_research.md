# File Research: sources/os/plan9/9front/sys/src/9/bcm64/clock.c

ARM64 BCM timer, cycle counter, and clock interrupt support.

Key responsibilities:
- Uses system timer 3 for CPU0 clock interrupts and `fastticks()`.
- Uses generic local timer interrupts for secondary CPUs.
- Initializes performance counter access and virtual counter access.
- Measures CPU frequency against the 1 MHz system timer.
- Programs next timer deadline in `timerset()`.
- Provides `fastticks()`, `perfticks()`, `microdelay()`, `delay()`, and `synccycles()`.

Important behavior:
- Treats `CNTFRQ_EL0` as unreliable on Raspberry Pi and sets cycle frequency to system timer frequency.
- Uses ARM timer for performance ticks and immediate wakeups.
- Panics on unexpected timer routing to the wrong CPU.

Dependencies:
- ARM64 system registers, interrupt registration, SoC oscillator frequency, timer core, and low-level cycle helpers.
