# File Research: sources/os/bsd/freebsd-src/sys/sys/cpuctl.h

## Purpose
Defines the `/dev/cpuctl` ioctl ABI for reading/writing MSRs, issuing CPUID, updating CPU microcode, and refreshing CPU feature evaluation.

## Main Elements
- `cpuctl_msr_args_t` carries MSR number and 64-bit data.
- `cpuctl_cpuid_args_t` carries CPUID level and four registers.
- `cpuctl_cpuid_count_args_t` adds CPUID level type/subleaf.
- `cpuctl_update_args_t` carries a user pointer and size for update data.
- Ioctls: `CPUCTL_RDMSR`, `CPUCTL_WRMSR`, `CPUCTL_CPUID`, `CPUCTL_UPDATE`, bit set/clear MSR ops, `CPUCTL_CPUID_COUNT`, `CPUCTL_EVAL_CPU_FEATURES`.

## Dependencies And Integration
Used by the cpuctl character device and privileged CPU management tools.

## Risk Notes
This ABI exposes privileged CPU state. Kernel handlers must validate CPU capabilities, permissions, update sizes, and architecture support.
