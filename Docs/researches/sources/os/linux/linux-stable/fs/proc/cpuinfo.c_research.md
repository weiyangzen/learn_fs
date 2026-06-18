# File Research: sources/os/linux/linux-stable/fs/proc/cpuinfo.c

## Purpose

Creates `/proc/cpuinfo` using architecture-provided seq operations.

## Main Responsibilities

- Declares external `cpuinfo_op`.
- `cpuinfo_open()` opens the file with `seq_open(file, &cpuinfo_op)`.
- Defines permanent proc operations for open/read/lseek/release.
- `proc_cpuinfo_init()` creates the `cpuinfo` proc entry.

## Notes

Formatting is architecture-owned through `cpuinfo_op`; this file only wires it into procfs.
