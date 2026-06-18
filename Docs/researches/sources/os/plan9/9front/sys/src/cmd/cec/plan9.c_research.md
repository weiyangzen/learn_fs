# File Research: sources/os/plan9/9front/sys/src/cmd/cec/plan9.c

Plan 9 raw Ethernet interface adapter for CEC.

Key behavior:
- `netopen0` opens `<iface>/clone`, connects to the CEC EtherType, opens control/data files, and makes the channel nonblocking.
- `netopen` wraps `netopen0`, prints errors, and closes partially opened fds on failure.
- `netclose` closes clone/control/data fds and resets globals.
- `netget` reads one frame and optionally dumps it under debug.
- `netsend` writes a frame, padding to minimum Ethernet payload size when needed.

Dependencies:
- Includes Plan 9 libc and `cec.h`.

Research notes:
- This is the platform-specific piece; the rest of CEC code uses `netget`/`netsend`.
