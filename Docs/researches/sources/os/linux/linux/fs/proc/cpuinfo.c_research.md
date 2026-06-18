# File Research: sources/os/linux/linux/fs/proc/cpuinfo.c

## Purpose
Registers `/proc/cpuinfo`, delegating architecture-specific CPU information rendering to the external `cpuinfo_op` seq operations.

## Main Responsibilities
- Opens `cpuinfo_op` with `seq_open()`.
- Defines proc operations using `seq_read_iter`, `seq_lseek`, and `seq_release`.
- Registers a permanent proc entry named `cpuinfo`.

## Key Interfaces
- `cpuinfo_open()`
- `cpuinfo_proc_ops`
- `proc_cpuinfo_init()`

## Dependencies and Integration
The actual content is provided by architecture-defined `cpuinfo_op`. This file supplies generic procfs registration and seq plumbing.

## Risks and Review Hotspots
- ABI content is architecture-specific, but registration and read behavior must remain stable.
- Entry is permanent, matching core procfs expectations.
