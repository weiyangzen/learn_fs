# File Research: sources/os/bsd/dragonflybsd/sys/sys/vnioctl.h

## Summary
Ioctl ABI for vnode-backed disk pseudo-devices.

## Main Responsibilities
- Defines default config path `/etc/vntab`.
- Defines attach/detach structure `struct vn_ioctl`.
- Defines query structure `struct vn_user` for file-backed and swap-backed vnode disk devices.
- Defines attach/detach, global/unit option, and get-info ioctl numbers.
- Defines debug, clustering, and swap-reservation option flags.

## Important Behavior
`vn_user` uses unions to represent either file-backed device/inode data or swap-backed size/sector-size data, with macros naming the active fields.

## Risks
The comment flags possible jail path disclosure through `vnu_file`. Userland and driver code must agree which union member is meaningful for the current backing mode.
