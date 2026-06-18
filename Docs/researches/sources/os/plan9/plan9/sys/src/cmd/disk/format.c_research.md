# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/format.c

Plan 9 disk/FAT formatting utility. It can format floppies, files, and disk partitions, write a Plan 9 boot sector, initialize FAT12/FAT16 filesystems, and copy initial root-directory files.

The file defines known disk `Type` geometries, DOS boot sector and root directory structures, a built-in nonbootable boot program, and global FAT/root allocation state. `main` parses options for boot block, cluster size, DOS/FAT mode, file creation, label, reserved sectors, disk type, verbosity, and safety bypass. It opens the disk through `opendisk`, infers type, optionally formats floppies through the control file, runs `sanitycheck`, dry-runs `dosfs`, then commits by running `dosfs` again.

`sanitycheck` protects against formatting a Plan 9 partition table sector without enough reserved sectors and against formatting an entire SCSI disk instead of a partition unless `-x` is used. `getdriveno` maps Plan 9 sd device names to BIOS drive numbers.

`dosfs` writes the boot sector/PBS and optionally initializes FAT. It sizes FAT12 vs FAT16 by iterating cluster and FAT-sector counts, writes BIOS parameter block fields, allocates in-memory FAT/root tables, copies requested files into the file area rounded to cluster boundaries, chains clusters with `clustalloc`, writes root directory entries with `addrname`, then writes both FAT copies and the root. `putname` formats 8.3 uppercase names, `puttime` writes DOS date/time, and `writen` throttles writes in 8 KiB chunks.

Integration points: uses Plan 9 `disk.h` `Disk` abstraction and standard `Dir` metadata. It is independent of the 9660 modules.

Risks and notes: FAT32 is explicitly unsupported. Initial files are read whole into memory. The dry-run/commit double call recalculates state and relies on deterministic sizing. A debug-style `fprint(2, "add ...")` is unconditional when adding files.
