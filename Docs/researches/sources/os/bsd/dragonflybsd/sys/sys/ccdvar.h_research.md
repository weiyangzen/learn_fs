# File Research: sources/os/bsd/dragonflybsd/sys/sys/ccdvar.h

Concatenated disk driver ABI and kernel state definitions for DragonFly’s CCD pseudo-disk.

Key responsibilities:
- Defines configuration inputs: `struct ccddevice` for initialization-time configuration and `struct ccd_ioctl` for ioctl-based user configuration.
- Defines CCD modes/flags: swap interleave, uniform interleave, mirroring, and parity.
- Describes component devices through `struct ccdcinfo`, including vnode, cdev, size, skip offset, and path.
- Defines irregular interleave groups in `struct ccdiinfo`.
- Defines pseudo-geometry and full `struct ccd_softc`, including component table, interleave table, devstat stats, disk overlay, raw cdev, mirror picker, and mirror locality blocks.
- Defines `CCDIOCSET` and `CCDIOCCLR` ioctls.

Dependencies:
- Includes `sys/conf.h`, `sys/devicestat.h`, `sys/disk.h`, `sys/diskslice.h`, and `sys/ioccom.h`.
- Uses vnode, cdev, lock, devstat, disk, and disk slice infrastructure.

Notable risks:
- `CCD_MAXNDISKS` allows very large component counts, so allocation and ioctl validation matter.
- User pointers in `ccd_ioctl` (`char **ccio_disks`) require careful copyin handling.
- Interleave and mirror logic depend on accurate component sizes and offset calculations.
