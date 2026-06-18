# File Research: sources/os/bsd/dragonflybsd/sys/sys/snoop.h

This header defines ioctl commands and error sentinel values for tty snooping support.

Key responsibilities:
- Includes ioctl command encoding definitions.
- Defines snoop ioctl commands:
  - `SNPSTTY`
  - `SNPGTTY`
- Defines negative `FIONREAD` sentinel returns:
  - `SNP_OFLOW`
  - `SNP_TTYCLOSE`
  - `SNP_DETACH`

Important invariants:
- `SNPSTTY` and `SNPGTTY` use `dev_t` as their ioctl payload type.
- Comments state setting type or unit to `-1` detaches the snoop device from its current tty, though the current command payload is `dev_t`.

Research notes:
- This is a narrow compatibility header for the snoop device interface.
