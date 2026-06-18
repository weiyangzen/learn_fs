# File Research: sources/os/bsd/dragonflybsd/sys/sys/devfs_rules.h

Devfs rule ioctl and kernel rule-application header.

Key responsibilities:
- Defines `struct devfs_rule` for in-kernel linked rules, including type/cmd, mount point, device name, link name, device type, mode, uid, gid, and queue link.
- Defines fixed-size `struct devfs_rule_ioctl` for userland ioctl exchange using `PATH_MAX` buffers.
- Defines rule selector bits for name, type, and jail.
- Defines rule command bits for link, hide, show, and permission changes.
- Defines ioctls to add, apply, clear, and reset rules.
- Declares kernel iteration callbacks to apply or reset rules on devfs nodes.

Dependencies:
- Includes `sys/ioccom.h`, `sys/queue.h`, and `sys/types.h`; kernel structures include `sys/devfs.h`.

Notable risks:
- Rule type and command bits overlap numerically by design but live in separate fields.
- Userland fixed path buffers must be validated and terminated before conversion to kernel pointer fields.
