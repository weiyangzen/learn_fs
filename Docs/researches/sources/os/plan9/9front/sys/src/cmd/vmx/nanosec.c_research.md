# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/nanosec.c

This file provides a monotonic-ish nanosecond timer for VM device emulation.

Key behavior:
- Prefers `cycles()` scaled by `_tos->cyclefreq` so time is not adjusted by wall-clock synchronization.
- Falls back to `nsec()` if cycle frequency is unavailable.
- Returns elapsed nanoseconds relative to first initialization.

Integration and risks:
- First call initializes state and returns zero.
- Timer users assume monotonic behavior for PIT/RTC/input watchdog scheduling.
