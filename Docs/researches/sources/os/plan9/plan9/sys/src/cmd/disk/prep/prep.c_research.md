# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/prep/prep.c

This file implements the Plan 9 partition-table editor for partitions inside a Plan 9 disk partition.

Key behavior:
- Opens a disk/partition with `opendisk`, optionally overrides sector size, checks for a FAT boot sector where the Plan 9 table would be, reads the Plan 9 partition table from sector 1, and enters generic edit mode.
- Partition table format is text lines: `part name start end`.
- `cmdadd` rejects non-`9fat` partitions starting before sector 2 to avoid the PBS/table area.
- `cmdokname` rejects control characters, space, slash, and DEL.
- `rdpart` parses the sector-1 table into `Part` records.
- `wrpart` writes the text table back to sector 1 and reconciles kernel sd ctl partitions through `ctldiff`.
- `restore` rewrites the saved old sector and attempts to restore ctl partitions after a failed write.
- `checkfat` refuses to overwrite a FAT boot sector signature at sector 1.
- `autoxpart` automatically allocates requested partition types according to min/max/weight rules.

Automatic partition names:
- `9fat`, `nvram`, `fscfg`, `fs`, `fossil`, `arenas`, `isect`, `bloom`, `other`, `swap`, `cache`.

Options:
- `-a partname`: request automatic partition.
- `-b`: blank existing table.
- `-c`, `-n`: accepted flags for cache/nvram mode state, though not otherwise used in the read code.
- `-f`: disk is a file.
- `-p`: print ctl commands read-only.
- `-r`: read-only.
- `-s sectorsize`: override sector size.
- `-w`: write after setup.

Notable detail:
- Editing unit is sector, unlike `fdisk.c` where unit is cylinder.
