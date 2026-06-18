# File Research: sources/os/plan9/9front/sys/src/9/omap/devarch.c

Implementation of the OMAP `#P` architecture device.

Key behavior:
- Provides dynamic architecture files via `addarchfile`.
- Implements Plan 9 device methods for attach, walk, stat, open, close, read, and write.
- Built-in files include `cputype`, `tb`, and `ns`.
- `cputyperead` reports the CPU name, clock, and architecture label.
- `tbread` exposes timebase information from `fastticks`.
- `nsread` reports nanosecond timing information.

Research notes:
- This is a small hardware-info and extension device, not a filesystem implementation.
- `archinit` installs the default arch files.
