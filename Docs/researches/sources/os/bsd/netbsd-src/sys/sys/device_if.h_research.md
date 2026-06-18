# File Research: sources/os/bsd/netbsd-src/sys/sys/device_if.h

Minimal public device type declarations used by many kernel and user-kmem headers.

Key content:
- Includes `<sys/stdint.h>`.
- Forward declares `struct device`.
- Defines `device_t` as `struct device *`.
- Under `_KERNEL` or `_KMEMUSER`, defines `devact_level_t`, `DEVACT_LEVEL_*`, forward declarations for device locks/suspensors, `devgen_t`, and related typedefs.

Important behavior:
- Keeps lightweight device identity available without pulling in the full autoconf framework.
- `DEVACT_LEVEL_FULL` aliases class-level activation.
