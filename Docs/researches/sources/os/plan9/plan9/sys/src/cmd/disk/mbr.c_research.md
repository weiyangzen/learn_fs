# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/mbr.c

This standalone disk utility installs or replaces PC master boot record boot code.

Key behavior:
- Defines DOS partition-table entry layout `Tentry`.
- Contains a built-in default MBR boot block that prints an error and reboots.
- `writechs` encodes CHS values, saturating cylinders at 1023.
- `wrtentry` writes an active partition entry with CHS and LBA fields.
- Opens a disk with `opendisk`, refuses floppies, reads the existing boot sector, and preserves the partition table unless `-9` rebuilds it.
- `-m mbrfile` uses external MBR code; otherwise uses the built-in default.
- `-9` creates one active Plan 9 partition of type `0x39`.
- Writes boot signature `0x55AA` and writes the MBR back.

Notable details:
- Assumes a 512-byte MBR area even on disks with larger sectors, relying on `/dev/sd` read-modify-write behavior.
- Writes whole-sector-rounded data length.
