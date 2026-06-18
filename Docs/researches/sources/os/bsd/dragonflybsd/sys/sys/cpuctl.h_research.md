# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpuctl.h

CPU control device ioctl ABI for MSR, CPUID, and microcode/update operations.

Key responsibilities:
- Defines payloads for reading/writing MSRs, issuing CPUID, issuing CPUID with count/level type, and passing update blobs.
- Defines ioctls for read/write MSR, CPUID, update, set/clear MSR bits, and CPUID_COUNT.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- MSR writes and CPU updates are privileged and security-sensitive; `caps.h` has capability restrictions for WRMSR and update.
- `cpuctl_update_args_t` carries a user pointer and length.
