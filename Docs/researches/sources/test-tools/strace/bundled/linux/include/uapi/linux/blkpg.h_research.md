<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/blkpg.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/blkpg.h

Purpose: block partition table ioctl UAPI definitions for `BLKPG`.

Important APIs/types: defines `BLKPG` ioctl number `_IO(0x12,105)`, `struct blkpg_ioctl_arg` with operation, flags, data length, and data pointer, operation constants `BLKPG_ADD_PARTITION`, `BLKPG_DEL_PARTITION`, `BLKPG_RESIZE_PARTITION`, name length constants, and `struct blkpg_partition` with byte start/length, partition number, and ignored name fields.

Control flow: declarations only.

State and persistence: ABI definitions for ioctls that can modify kernel partition state when used on real block devices.

Dependencies and integration: includes `<linux/ioctl.h>` and feeds strace ioctl decoders.

Risks: pointer member in `blkpg_ioctl_arg` requires decoder to follow user memory safely and respect `datalen`. Test signals: ioctl decoder tests should print operation names and nested partition fields for BLKPG calls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/blkpg.h -->
