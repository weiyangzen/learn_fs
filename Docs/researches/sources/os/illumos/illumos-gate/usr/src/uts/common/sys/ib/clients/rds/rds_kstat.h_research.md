# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds_kstat.h

This header defines legacy RDS kstats and convenience macros for updating them.

Core definitions:
- `struct rds_kstat_s` exposes counters/gauges for ports, sessions, TX/RX bytes and packets, errors, pending RX packets, ACKs, post-receive calls, stall/unstall events, ignored stalls, ENOBUFS, EWOULDBLOCK, failovers, port quota, and quota adjustments.
- Generic helpers increment, decrement, set, and get `kstat_named_t` values with a boolean likely indicating whether the value is a mutable gauge.
- Macros wrap every named statistic update.

Risk-sensitive invariants:
- Pending packet and port count stats are decremented as gauges; traffic/error stats are monotonic counters.
- Correct flow-control diagnosis depends on stall/unstall and pending-packet stats being updated in all paths.
