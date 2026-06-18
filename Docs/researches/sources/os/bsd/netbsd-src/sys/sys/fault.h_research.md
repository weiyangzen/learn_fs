# File Research: sources/os/bsd/netbsd-src/sys/sys/fault.h

Read completely: 79 lines.

## Purpose
Defines fault-injection control ABI and the kernel `fault_inject` hook.

## Main Interfaces
- Scopes: `FAULT_SCOPE_GLOBAL`, `FAULT_SCOPE_LWP`.
- Mode: `FAULT_MODE_NTH_ONESHOT`.
- Minimum nth trigger: `FAULT_NTH_MIN`.
- Ioctl payloads: `fault_ioc_enable`, `fault_ioc_disable`, `fault_ioc_getinfo`.
- Ioctls: `FAULT_IOC_ENABLE`, `FAULT_IOC_DISABLE`, `FAULT_IOC_GETINFO`.
- Kernel hook: `fault_inject()` real when `FAULT` is configured, otherwise inline false.

## Dependencies And Integration
Includes `opt_fault.h` in kernel option builds and uses ioctl encoding.

## Risks And Edge Cases
- User-visible ioctls are available only outside kernel or with `FAULT`.
- Non-FAULT kernels compile fault checks away to false.

## Filesystem Relevance
Moderate for testing. Fault injection can exercise filesystem error paths if used by lower layers.
