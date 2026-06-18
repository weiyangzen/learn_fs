# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vt.h

## Role

`vt.h` defines the public virtual-terminal ioctl interface shared with other operating systems plus Solaris-specific console-user and display metadata operations.

## Key Interfaces

Public ioctls include:
- `VT_OPENQRY`
- `VT_SETMODE`
- `VT_GETMODE`
- `VT_RELDISP`
- `VT_ACTIVATE`
- `VT_WAITACTIVE`
- `VT_GETSTATE`
- `VT_ENABLED`
- `VT_GET_CONSUSER`
- `VT_SET_CONSUSER`

`struct vt_mode` configures automatic vs process-controlled switching, write-wait behavior, and signals for release/acquire/forced release.

`struct vt_stat` returns active VT, signal, and open-state mask.

Project-private ioctls configure VT count, display info/login state, target console, real active console, and console-user reset.

`struct vt_dispinfo` carries display owner PID, display number, and login state.

## Research Notes

The header separates public compatibility ioctls from illumos/private control ioctls. `VT_SET_TARGET` and `VT_GETACTIVE` exist to hide the vtdaemon special console from ordinary `VT_GETSTATE` consumers.
