# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_cctr.c

Read completely: 288 lines.

Implements a CPU cycle-counter-backed `timecounter` and multiprocessor calibration support. The primary CPU is treated as the reference counter; secondary CPUs maintain `ci_cc.cc_delta` offsets so `cc_get_timecount()` can return a primary-relative counter value.

`cc_init()` initializes the global `cc_timecounter`, optionally installs an MD counter reader, records frequency/name/quality, initializes the MP calibration spin mutex, and registers the timecounter. `cc_init_secondary()` seeds per-secondary calibration counters with CPU-index skew and immediately calibrates. `cc_calibrate_cpu()` serializes calibration attempts, triggers the primary CPU via `cc_get_primary_cc()`, waits for the primary-ready state, and retries if the secondary’s 32-bit counter wraps during measurement. `cc_primary_cc()` is the primary-side rendezvous routine that publishes the reference counter value.

The MP calibration protocol uses atomic release/acquire state transitions among `CC_CAL_START`, `CC_CAL_PRIMARY_READY`, `CC_CAL_SECONDARY_READY`, and `CC_CAL_FINISHED`. `cc_get_delta()` samples the secondary counter before and after the primary reference point, computes an overflow-safe midpoint, and stores the delta.

Risks and notes: calibration uses busy waits and expects primary-side interrupts to be blocked when `cc_primary_cc()` runs. A 32-bit counter wrap during the secondary measurement forces retry. The source notes that `cc_timecounter.tc_frequency` is not sysctl-adjustable and that variable-frequency counters should not be auto-selected without care.
