# File Research: sources/os/bsd/freebsd-src/sys/sys/mouse.h

Defines mouse device ioctl ABI, status/mode/hardware structures, protocol identifiers, model identifiers, and packet-format constants.

Key content:
- Ioctls for status, hardware info, mode get/set, protocol level get/set, raw state/data reads, and Synaptics hardware info.
- `mousestatus_t` tracks state-change flags, current/previous buttons, and dx/dy/dz movement.
- Button masks support up to 31 buttons, with standard and extended button masks.
- `mousehw_t` reports button count, interface type, device type, model, and hardware id.
- `synapticshw_t` exposes many Synaptics capability and geometry fields.
- Defines interface types: unknown, serial, PS/2, sysmouse, USB.
- Defines device types: mouse, trackball, stick, pad.
- Defines models including generic, GlidePoint, IntelliMouse, Think, VersaPad, Explorer, Synaptics, TrackPoint, Elantech.
- `mousemode_t` stores protocol, rate, resolution, acceleration, level, packet size, and sync mask.
- Protocol constants cover serial, PS/2, sysmouse, remote, VersaPad, jogdial, GTCO, and legacy bus/inport.
- Extensive packet constants document packet sizes, sync masks, button bits, sign/overflow bits, wheel bits, and sysmouse extended packet layout.
- Defines `_PATH_MOUSEREMOTE`.

Research relevance:
- Peripheral/device ABI rather than filesystem-specific, but part of the FreeBSD sys header group.
- Useful for understanding userland ioctl compatibility and input-device packet decoding.

Cautions:
- Several bus protocols are marked obsolete in comments.
- Packet bit definitions vary by protocol and sometimes reuse bits, e.g. PS/2 GlidePoint tap uses the sync bit.
