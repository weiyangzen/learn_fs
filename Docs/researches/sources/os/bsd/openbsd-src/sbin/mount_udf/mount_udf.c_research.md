# File Research: sources/os/bsd/openbsd-src/sbin/mount_udf/mount_udf.c

`mount_udf.c` mounts UDF filesystems. It parses shared `-o` options, resolves the mount point, fills `struct udf_args`, and calls `mount(MOUNT_UDF, ...)`.

The helper computes `args.lastblock` by opening the device and issuing `CDIOREADTOCENTRIES` for the lead-out track LBA. If that ioctl fails, it returns zero for last block.

This is optical-media-oriented glue around the kernel UDF mount interface.
