# File Research: sources/local-fs/dosfstools/src/blkdev/blkdev.c

Portable block-device helper implementation, mostly used by mkfs/device discovery.

Main behavior:
- `is_blkdev()` uses `fstat()` and `S_ISBLK`.
- `blkdev_find_size()` probes readable offsets with exponential search followed by binary search.
- `blkdev_get_size()` tries platform-specific size APIs in order:
  - Darwin `DKIOCGETBLOCKCOUNT`
  - Linux `BLKGETSIZE64`, guarded against known broken 2.4 kernels
  - Linux `BLKGETSIZE`
  - FreeBSD `DIOCGMEDIASIZE`
  - floppy `FDGETPRM`
  - older FreeBSD disklabel `DIOCGDINFO`
  - regular-file `st_size`
  - fallback probing for block devices.
- `blkdev_get_sectors()` returns 512-byte sector count.
- `blkdev_get_sector_size()` uses `BLKSSZGET` or defaults to 512.
- `blkdev_get_physector_size()` uses `BLKPBSZGET` where available or defaults to 512.
- `blkdev_is_misaligned()` checks `BLKALIGNOFF`.
- `blkdev_is_cdrom()` checks `CDROM_GET_CAPABILITY`.
- `blkdev_get_geometry()` uses `HDIO_GETGEO` or floppy geometry.
- `blkdev_get_start()` uses Linux sysfs `/sys/dev/block/<maj>:<min>/start`, falling back to `HDIO_GETGEO`.
- `blkdev_scsi_type_to_name()` maps SCSI peripheral type constants to strings.

Notable implementation details:
- The file is public-domain imported utility code.
- It conditionally supports Linux, Darwin, FreeBSD, Solaris-style headers, and floppy devices.
- `blkdev_get_physector_size()` calls `ioctl(fd, BLKPBSZGET, &sector_size)`, passing an `int **` rather than the `int *` parameter. That looks suspicious and should be reviewed before relying on physical-sector reporting.
