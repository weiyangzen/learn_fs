# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msacct.h

Microstate accounting constants for LWPs and CPUs.

Key responsibilities:
- Defines LWP microstates for user, system, trap, user/kernel page faults, user lock wait, sleep, CPU wait, and stopped states.
- Defines `NMSTATES` as the number of LWP microstates, with a comment warning it must not exceed the `siginfo` size constraint.
- Defines CPU microstates for user, system, idle, and disabled.
- Defines `NCMSTATES` as 3 because disabled CPUs are not accounted as a normal CPU accounting state.

Dependencies:
- Referenced by accounting, `/proc`, scheduling, and CPU state reporting code.

Notable risks:
- Numeric state values are ABI/signaling data; reordering or expanding them affects accounting consumers.
- `NMSTATES` has an explicit structural size constraint through `struct siginfo`.
