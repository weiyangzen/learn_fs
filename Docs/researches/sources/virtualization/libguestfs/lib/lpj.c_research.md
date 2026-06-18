# File Research: sources/virtualization/libguestfs/lib/lpj.c

Calculates host kernel `loops_per_jiffy` for TCG appliances.

Important behavior:
- `guestfs_int_get_lpj` computes once under a process-wide mutex and caches the result.
- Attempts to find `lpj=NNN` first from `dmesg`, then from readable boot log files `/var/log/dmesg` and `/var/log/boot.msg`.
- Uses grep through libguestfs command helpers and reads the whole command output via callback.
- Failures are intentionally non-fatal; callers ignore non-positive results.
- Parses the value after `lpj=` and logs debug details on invalid output or command status.

Filesystem relevance:
- Optimizes appliance boot under emulation, reducing launch overhead before filesystem inspection.
