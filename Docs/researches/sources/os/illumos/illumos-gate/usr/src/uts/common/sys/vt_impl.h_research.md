# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vt_impl.h

## Role

`vt_impl.h` defines the kernel-private state and functions for the virtual console/terminal implementation.

## Key Structures

`vc_waitactive_msg_t` queues pending `VT_WAITACTIVE` messages with source minor, target minor, and STREAMS message pointer.

`vc_state_t` is the per-VT soft state. It stores:
- minor number and AVL linkage,
- switching mode, wait flag, release/acquire signals, controlling PID, target switch minor, and flags,
- display number and login state,
- terminal emulator state and tty common state,
- STREAMS bufcall/timeout IDs and write queue,
- optional pending firmware character,
- a mutex protecting `vc_flags`.

Flags cover tty initialization, open state, stopped output, delay, and busy transmission.

## Integration Points

The header declares ioctl/open/close/cleanup functions, hotkey checking, minor-to-state lookup, global VT state variables, attachment/init helpers, active/console-user string helpers, minor validation, and resize support.

Global state includes the wscons device info pointer, AVL root of VTs, active console, console-user target, global lock, and last console.

## Research Notes

This header is internal to console STREAMS/VT code and depends on `vt.h`, keyboard/display headers, terminal emulator state, tty common state, AVL, and list infrastructure.
