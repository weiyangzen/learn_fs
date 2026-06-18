# File Research: sources/os/plan9/9front/sys/src/cmd/disk/format.c

Disk/floppy/file FAT formatter and boot-sector writer.

Key behavior:
- Supports floppy geometries, hard disks, and file-backed images.
- Can write a Plan 9 boot sector/program, initialize FAT12/FAT16/FAT32 structures, and add root-directory files.
- Parses options for boot block, cluster size, label, reserved sectors, disk type, file creation, DOS/FAT mode, verbosity, and safety override.
- `sanitycheck` guards against formatting whole disks or clobbering Plan 9 partition tables without explicit override.
- `dosfs` computes FAT size, root directory size, cluster count, FAT type, BIOS parameter block fields, FAT info sector, FAT tables, root directory, and file data.
- Long filenames are emitted through VFAT long-name slots with generated 8.3 aliases.
- `clustalloc` writes FAT12/16/32 chains.

Notable dependencies:
- Plan 9 `disk.h` and `opendisk`.
- Embedded x86 boot stub that prints a not-bootable message.

Research notes:
- Performs a dry run before commit to catch errors.
- The code has duplicated `fatsecs` global declaration in the file.
- Adds files only to the root directory; it is not a general recursive FAT builder.
