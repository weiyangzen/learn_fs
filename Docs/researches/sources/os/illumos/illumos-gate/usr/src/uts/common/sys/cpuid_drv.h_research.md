# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpuid_drv.h

## Role

Defines names, minor values, ioctls, and data structures for the `/dev/cpu/.../cpuid` driver interface.

## Device Names

- Driver: `cpuid`
- Self node: `self`
- Directory names:
  - `cpu`
  - `self`
  - `cpuid`
- `CPUID_SELF_NAME`: `cpu/self/cpuid`

## Minor and Ioctls

- `CPUID_SELF_CPUID_MINOR`: special minor for current CPU at invocation time.
- `CPUID_IOC`: ioctl base.
- `CPUID_GET_HWCAP`
- `CPUID_RDMSR`

The file notes ioctl numbers are not exported interfaces.

## Data Structures

- `struct cpuid_get_hwcap`:
  - architecture name pointer.
  - three hardware capability words.
- `struct cpuid_rdmsr`:
  - MSR number.
  - MSR value.
- `_SYSCALL32_IMPL` variant:
  - `struct cpuid_get_hwcap32`.

## Research Relevance

Small but useful for user/kernel CPU identification and MSR access plumbing.
