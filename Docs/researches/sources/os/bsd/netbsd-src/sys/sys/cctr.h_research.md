# File Research: sources/os/bsd/netbsd-src/sys/sys/cctr.h

## Scope

Declares cycle-counter timecounter state and calibration hooks.

## APIs And Data Structures

- `cctr_state` stores CPU cycle-counter delta, calibration interval, and ticks since calibration.
- Kernel APIs include `cc_init`, `cc_init_secondary`, `cc_get_timecount`, `cc_calibrate_cpu`, and `cc_primary_cc`.
- `cc_hardclock(ci)` increments per-CPU calibration ticks and triggers calibration when the interval is reached.

## Dependencies

- Includes `sys/timetc.h`; uses `struct cpu_info`.

## Risks And Invariants

- `cc_delta` is volatile and used across CPU timecounter calibration paths.
- `cc_hardclock` assumes `ci->ci_cc` layout exists in `cpu_info`.
