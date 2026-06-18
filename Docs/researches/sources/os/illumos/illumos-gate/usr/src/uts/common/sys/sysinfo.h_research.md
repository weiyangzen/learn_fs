# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysinfo.h

## Purpose
Defines kernel CPU, system, and VM accounting structures exported through kstats and historical system statistics interfaces.

## Main Interfaces
- State constants:
  - `CPU_IDLE`, `CPU_USER`, `CPU_KERNEL`, `CPU_WAIT`, `CPU_STATES`
  - wait-state constants `W_IO`, `W_SWAP`, `W_PIO`, `W_STATES`
- Legacy/stat structures:
  - `cpu_sysinfo_t`
  - `sysinfo_t`
  - `cpu_syswait_t`
  - `cpu_vminfo_t`
  - `vminfo_t`
  - `cpu_stat_t`
- 64-bit kstat-oriented structures:
  - `cpu_sys_stats_t`
  - `cpu_vm_stats_t`
  - `cpu_stats_t`

## Dependencies And Relationships
Includes `sys/types.h`, `sys/t_lock.h`, `sys/kstat.h`, and `sys/machlock.h`. Filesystems and VM paths increment counters such as block reads/writes, name lookups, UFS inode stats, paging, COW faults, and filesystem page activity.

## Research Notes
This is an accounting ABI, not logic. Several fields are retained as unused/compatibility counters, and comments document how tools like `sar(1)` interpret logical vs physical read/write counters.
