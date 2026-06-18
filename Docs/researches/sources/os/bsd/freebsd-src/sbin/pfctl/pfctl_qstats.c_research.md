# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_qstats.c

## Purpose
Implements `pfctl` ALTQ queue statistics display and live rate sampling.

## Main Elements
- Maintains an in-memory tree of `pf_altq_node` entries with child queues and `queue_stats`.
- `pfctl_show_altq()` loads current ALTQ stats, prints queues, and optionally repeats every five seconds for verbose live output.
- `pfctl_update_qstats()` fetches queues and scheduler-specific stats through `DIOCGETALTQS`, `DIOCGETALTQ`, and `DIOCGETQSTATS`.
- Scheduler-specific printers cover CBQ, CoDel, PRIQ, HFSC, and FAIRQ counters.
- `update_avg()` computes smoothed packet/byte deltas for measured rates.

## Dependencies And Integration
Uses PF ioctls, ALTQ scheduler stat structures, and shared pfctl formatting helpers such as `print_altq()` and `rate2str()`.

## Risk Notes
Scheduler-specific union interpretation must match kernel-provided versions. Live average calculation depends on monotonic counter increases and fixed `STAT_INTERVAL`.
