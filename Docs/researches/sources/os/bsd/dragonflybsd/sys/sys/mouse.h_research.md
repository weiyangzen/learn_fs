# File Research: sources/os/bsd/dragonflybsd/sys/sys/mouse.h

Public mouse ioctl and packet-format interface for DragonFlyBSD mouse, sysmouse, PS/2, serial, USB, and touchpad consumers.

Key responsibilities:
- Defines userland-visible mouse ioctls: `MOUSE_GETSTATUS`, `MOUSE_GETHWINFO`, `MOUSE_GETMODE`, `MOUSE_SETMODE`, `MOUSE_GETLEVEL`, `MOUSE_SETLEVEL`, `MOUSE_READSTATE`, `MOUSE_READDATA`, and Synaptics hardware info query.
- Defines status, hardware, Synaptics capability, mode, and data-buffer structures.
- Enumerates button bitmasks through 31 buttons and state-change flags.
- Defines interface, device type, model, protocol, resolution, packet size, sync mask, and button-bit constants for many legacy and modern mouse protocols.
- Documents `/dev/sysmouse` level-0 and level-1 packet layout and remote socket path `_PATH_MOUSEREMOTE`.

Important behavior:
- This header is ABI material: ioctl numbers and structure layouts are consumed by drivers and userland tools.
- `mousestatus_t` reports deltas and button transitions; `mousemode_t` describes report protocol framing.
- Protocol definitions cover Microsoft serial, Mouse Systems, MM series, PS/2, IntelliMouse, Explorer, VersaPad, A4 Tech 4D, Synaptics, Elantech, and sysmouse.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.
- Used by mouse drivers, console/sysmouse layers, and userland programs that inspect or configure pointer devices.

Notable risks:
- Many constants encode hardware packet bits directly; mistakes break driver decoding or userland compatibility.
- `synapticshw_t` is a large flat capability ABI with no explicit version field.
- Several legacy protocols have inverted button semantics, especially Mouse Systems/sysmouse `UP` bits.
