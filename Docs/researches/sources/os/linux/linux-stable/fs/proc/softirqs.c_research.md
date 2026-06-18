# File Research: sources/os/linux/linux-stable/fs/proc/softirqs.c

Implements `/proc/softirqs`.

Key points:
- Formats per-CPU counts for each softirq type.
- Header lists possible CPUs; rows use `softirq_to_name[]` and `kstat_softirqs_cpu()`.
- Registers `softirqs` as a permanent single proc file.

Dependencies/contracts:
- Exposes kernel softirq accounting in the standard text format.
