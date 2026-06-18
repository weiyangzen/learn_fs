# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/filio.h

Defines general file ioctl numbers using `sys/ioccom.h`. Standard ioctls include `FIOCLEX`, `FIONCLEX`, `FIONREAD`, `FIONBIO`, `FIOASYNC`, `FIOSETOWN`, and `FIOGETOWN`.

The rest are mostly illumos/UFS/private filesystem ioctls: filesystem lock/status/flush, obsolete allocation info, atime setting, delayed I/O get/set, inode open, DiskSuite/UFS logging protocols, busy/directio/tuning controls, logging enable/disable, UFS snapshot create/delete including multi-backing-file snapshot creation, superblock retrieval, maxphys query, TSufs debug/error/stats controls, SEEK_DATA/SEEK_HOLE implementation ioctls, boot archive compression marking, and filled-region counting.

This file is user-visible ioctl ABI. Numeric values should be considered stable even for obsolete/private operations.
