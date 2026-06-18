# File Research: sources/os/plan9/9front/sys/src/9/port/dtracytimer.c

Implements the `dtracy` timer provider. It creates one probe, `timer::1tk`, and triggers it from `dtracytick`.

When enabled, `running` is set and each tick records the interrupted program counter in `arg[0]` and whether the register frame is user mode in `arg[1]`. Disabling clears `running`. This is a minimal sampling hook intended to be called from architecture timer interrupt code.
