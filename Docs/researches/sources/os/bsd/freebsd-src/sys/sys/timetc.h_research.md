# File Research: sources/os/bsd/freebsd-src/sys/sys/timetc.h

Kernel timecounter hardware interface header.

Key responsibilities:
- Defines `struct timecounter`, including callbacks to read the counter, poll PPS, fill native/32-bit vDSO timehands, counter mask, frequency, name, quality, flags, private pointer, and registration linkage.
- Documents timecounter requirements: fixed known frequency and sufficient width to avoid rapid rollover.
- Defines flags for C2-stop and suspend-safe behavior.
- Declares global current timecounter and minimum ticktock frequency.
- Declares timecounter frequency, initialization, clock-set, ticktock, CPU tick calibration, and clock calibration helpers.
- Exposes `_kern_timecounter` sysctl tree when available.

Dependencies:
- Kernel-only; depends on `u_int`, `timespec`, vDSO timehands types, and machine-dependent vDSO support.

Notable risks:
- Timecounter quality and flags directly affect system clock source selection and suspend/idle correctness.
- vDSO fill callbacks must be consistent with hardware capabilities or userland fast time reads can become wrong.
