# File Research: sources/os/bsd/dragonflybsd/sys/sys/disklabel64.h

DragonFly 64-bit byte-offset disklabel on-disk format and ioctl ABI.

Key responsibilities:
- Defines 64-bit label magic, active/reserved partition counts, and reserved boot2 size.
- Defines `struct disklabel64` starting with 512 reserved bytes, followed by magic, CRC, alignment, partition count, storage UUID, total size, boot/base/stop/backup offsets, pack name, reserved space, and partition table.
- Defines `struct partition64` with slice-relative byte offset/size, filesystem type, reserved zero fields, type UUID, and storage UUID.
- Declares kernel `disklabel64_ops`.
- Defines ioctls to get, set, write, and get virgin 64-bit labels.

Dependencies:
- Includes types, optional kernel systm, ioccom, and uuid.

Notable risks:
- All offsets are slice-relative bytes, unlike 32-bit labels; conversion bugs can corrupt partition bounds.
- The first 512 bytes are excluded from CRC and preserved on writeback.
- Active partition limit is 16 while virgin-label space reserves room for 32.
