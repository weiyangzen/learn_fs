# File Research: sources/os/linux/linux-stable/fs/proc/stat.c

Implements `/proc/stat`.

Key points:
- Exports aggregate and per-online-CPU cputime counters.
- Uses `get_cpu_idle_time_us()` and `get_cpu_iowait_time_us()` when available, otherwise falls back to cpustat.
- Includes interrupt totals, per-IRQ counts with gaps zero-filled, context switches, boot time, forks, runnable and iowait task counts, and softirq totals.
- Applies time namespace boot-time adjustment with `timens_sub_boottime()`.
- `stat_open()` sizes seq buffer based on online CPUs and IRQ count.
- Registers `stat` as permanent and uses `seq_read_iter`.

Dependencies/contracts:
- Stable userspace ABI for system accounting tools.
- Uses scheduler, IRQ, cputime, tick, and time namespace data.
