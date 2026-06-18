# File Research: sources/os/linux/linux-stable/fs/proc/Makefile

## Purpose

Builds the procfs composite object and conditionally includes procfs feature objects.

## Main Contents

- Always builds `proc.o`.
- Selects memory-management implementation:
  - `nommu.o task_nommu.o` by default.
  - `task_mmu.o` when `CONFIG_MMU=y`.
- Always included proc components:
  - `inode.o`, `root.o`, `base.o`, `generic.o`, `array.o`, `fd.o`.
  - Global proc files: `cmdline.o`, `consoles.o`, `cpuinfo.o`, `devices.o`, `interrupts.o`, `loadavg.o`, `meminfo.o`, `stat.o`, `uptime.o`, `util.o`, `version.o`, `softirqs.o`, `namespaces.o`, `self.o`, `thread_self.o`.
- Conditional components:
  - `proc_tty.o` under `CONFIG_TTY`.
  - `proc_sysctl.o` under `CONFIG_PROC_SYSCTL`.
  - `proc_net.o` under `CONFIG_NET`.
  - `kcore.o` under `CONFIG_PROC_KCORE`.
  - `vmcore.o` under `CONFIG_PROC_VMCORE`.
  - `kmsg.o` under `CONFIG_PRINTK`.
  - `page.o` under `CONFIG_PROC_PAGE_MONITOR`.
  - `bootconfig.o` under `CONFIG_BOOT_CONFIG`.

## Notes

This file ties the source files in this research group into the procfs build, especially `base.o`, `generic.o`, `array.o`, and `fd.o`.
