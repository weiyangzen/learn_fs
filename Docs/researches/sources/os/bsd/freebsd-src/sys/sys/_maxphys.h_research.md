# File Research: sources/os/bsd/freebsd-src/sys/sys/_maxphys.h

Default maximum physical I/O size definition.

Key elements:
- Defines `MAXPHYS` if not already set.
- Uses `128 KiB` for `__ILP32__`, otherwise `1 MiB`.

Dependencies:
- None.

Research notes:
- Public-domain compatibility shim.
- Directly relevant to block and filesystem I/O sizing defaults.
