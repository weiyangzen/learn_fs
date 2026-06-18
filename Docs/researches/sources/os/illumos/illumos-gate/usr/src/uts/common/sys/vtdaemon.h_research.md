# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtdaemon.h

## Role

`vtdaemon.h` defines the small door-based interface used to communicate with the virtual-terminal daemon.

## Key Interfaces

The daemon door path is:
- `/var/run/vt/vtdaemon_door`

Event codes:
- `VT_EV_X_EXIT`, carrying a VT number.
- `VT_EV_HOTKEYS`, carrying a VT number.

`vt_cmd_arg_t` contains the event code and VT number.

## Research Notes

This header is intentionally minimal and is paired with the VT implementation and daemon. It defines control-plane messages, not terminal data.
