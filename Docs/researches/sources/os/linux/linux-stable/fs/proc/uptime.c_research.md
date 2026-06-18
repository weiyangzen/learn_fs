# File Research: sources/os/linux/linux-stable/fs/proc/uptime.c

Implements `/proc/uptime`.

Key points:
- Sums idle time across possible CPUs using `kcpustat_cpu_fetch()` and `get_idle_time()`.
- Reads boottime with `ktime_get_boottime_ts64()`.
- Applies time namespace adjustment with `timens_add_boottime()`.
- Prints uptime and aggregate idle time with two decimal places.
- Registers `uptime` as a permanent single proc file.

Dependencies/contracts:
- Uses `get_idle_time()` exported by `stat.c`.
- Time namespace aware.
