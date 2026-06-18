# File Research: sources/os/plan9/9front/sys/src/cmd/disk/mbr.c

PC master boot record installer.

Key behavior:
- Reads the existing first sector, replaces boot code from either an embedded default MBR or `-m mbrfile`, preserves the partition table unless `-9` is requested, and writes the MBR signature.
- `-9` clears the partition table and creates one active Plan 9 partition of type `0x39` starting after the first track.
- Handles CHS encoding with saturation at cylinder 1023 and writes little-endian LBA/size fields.
- Refuses to install on floppy disks.

Notable dependencies:
- Plan 9 `disk.h`/`opendisk`.

Research notes:
- For non-512-byte media, it still operates on 512-byte MBR content and relies on the device layer for safe sector handling.
