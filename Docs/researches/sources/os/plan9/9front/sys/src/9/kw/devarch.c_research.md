# File Research: sources/os/plan9/9front/sys/src/9/kw/devarch.c

Implements the `#P` architecture device.

Key elements:
- Maintains a fixed table of architecture-specific files with read/write callbacks.
- Provides `addarchfile` for registering permanent files.
- Implements standard Plan 9 device attach/walk/stat/open/read/write methods.
- Registers `cputype` and `timebase` files at init.
- Formats CPU/SoC identity using CPUID and PCIe/device ID registers.
- Exposes the cycle counter through `timebase`.

Dependencies:
- Uses Plan 9 device framework, `soc`, PCIe register structures, `cpidget`, and cycle counter helpers.

Research notes:
- The device table is limited to 16 entries.
- CPU naming is Marvell/Kirkwood-specific and records SoC revision for later platform use.
