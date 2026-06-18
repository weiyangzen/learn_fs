# File Research: sources/os/bsd/dragonflybsd/sys/sys/conf.h

Kernel character-device, line-discipline, and swap-device configuration header.

Key responsibilities:
- Defines `struct cdev`, including ownership/perms, major/minor, parent, hash links, vnode lists, name, driver private pointers, dev_ops pointers, I/O size, sysref, tty/disk union, bio tracking, timestamps, pager object, property dictionary, and kqueue info.
- Defines `si_flags` values for hash state, permission override, dev_ops interception, devfs linkage, reprobe, and free-block support.
- Defines line discipline function typedefs and `struct linesw`.
- Defines `struct swdevt` for swap device accounting and vnode/cdev linkage.
- Declares kernel helpers for line discipline registration, device references/destruction/name lookup, zero-device check, minor extraction, and disk lookup by name.
- Defines default UID/GID constants used by device creation.

Dependencies:
- Kernel/kernel-structures only; includes queue, time, biotrack, sysref, event, proplib, and param headers.
- Uses dev_ops from `device.h` indirectly and vnode/disk/vm_object forward declarations.

Notable risks:
- `struct cdev` is central shared kernel state for devfs, disk, tty, pager, and kqueue paths; layout changes have broad blast radius.
- Multiple subsystems rely on the tty/disk union fields being interpreted correctly for the device type.
