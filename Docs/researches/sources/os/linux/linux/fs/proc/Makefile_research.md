# File Research: sources/os/linux/linux/fs/proc/Makefile

## Purpose
Build rules for procfs objects.

## Main Behavior
- Builds the procfs composite object via `obj-y += proc.o`.
- Selects `task_mmu.o` when `CONFIG_MMU` is enabled, otherwise `nommu.o` and `task_nommu.o`.
- Always includes core files such as `inode.o`, `root.o`, `base.o`, `generic.o`, `array.o`, `fd.o`, and common `/proc` files (`cmdline`, `consoles`, `cpuinfo`, `devices`, etc.).
- Conditionally includes objects for TTY, sysctl, networking, kcore, vmcore, printk kmsg, page monitor, and bootconfig.

## Dependencies and Integration
Directly reflects Kconfig choices from `fs/proc/Kconfig` and other subsystem configs. This Makefile defines the compiled surface area of procfs.

## Risks and Review Hotspots
- Object inclusion determines whether sensitive proc entries exist.
- `task_mmu.o` receives `-Wno-override-init`, indicating known initializer patterns in that file.
- Conditional object coverage must match declarations used by `base.c` and other procfs files.
