# File Research: sources/os/bsd/netbsd-src/sys/sys/cpuio.h

Defines user/kernel ioctl ABI for CPU state control and CPU microcode updates.

Key content:
- `cpustate_t` contains CPU id, online/intr flags, last modification time split fields, name, interrupt count, hardware id, and reserved fields.
- Ioctls: `IOC_CPU_SETSTATE`, `IOC_CPU_GETSTATE`, `IOC_CPU_GETCOUNT`, `IOC_CPU_MAPID`.
- Microcode version structure `cpu_ucode_version`.
- i386-specific 64-bit compatibility structure for amd64 kernels.
- `struct cpu_ucode` with loader version, CPU selector, firmware name.
- CPU selector constants: `CPU_UCODE_ALL_CPUS`, `CPU_UCODE_CURRENT_CPU`.
- Ioctls: `IOC_CPU_UCODE_GET_VERSION`, `IOC_CPU_UCODE_APPLY`.

Important behavior:
- Includes `PATH_MAX` for firmware name sizing outside the kernel.
- Stable ABI for `/dev/cpu`-style control paths.
