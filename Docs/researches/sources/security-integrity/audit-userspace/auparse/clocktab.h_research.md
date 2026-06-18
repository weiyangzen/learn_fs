# sources/security-integrity/audit-userspace/auparse/clocktab.h

Purpose: Build-time table mapping Linux clock IDs to symbolic clock names.

Important APIs, types, and functions: `_S()` rows cover `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, CPU-time clocks, raw/coarse clocks, boottime/alarm clocks, `CLOCK_SGI_CYCLE`, and `CLOCK_TAI`. `Makefile.am` generates `clocktabs.h` with `gen_clock_h --i2s clock`.

Control flow: No runtime flow.

State and persistence: Static table source for generated lookup code.

Dependencies and integration points: Based on `include/uapi/linux/time.h`; used by auparse interpretation of clock-related syscall fields.

Risks and edge cases: New clock IDs need table updates. Platform-specific IDs may not be represented.

Test signals: Generated table build and field interpretation tests for clock IDs.
