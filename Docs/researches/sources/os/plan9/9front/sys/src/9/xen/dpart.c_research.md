# File Research: sources/os/plan9/9front/sys/src/9/xen/dpart.c

Boot-time disk partition discovery helper.

Purpose:
- Scans disks under `#S`, creates Plan 9 partition entries, then execs `/boot/boot2`.

Key behavior:
- Reads disk sectors with `readdisk` and writes partition definitions through each disk control file.
- Detects DOS/FAT and extended MBR partition types.
- `mbrpart` handles MBR, DMDDO offset, extended partition chains, Plan 9 partitions, and first DOS partition.
- `p9part` opens a Plan 9 partition and parses its textual partition table.
- `cdpart` detects El Torito boot floppy images and adds `cdboot`.
- `partall` binds console FDs, scans `#S/*/data`, and runs partition recognizers.

Filesystem relevance:
- Directly prepares block-device partition namespace before the second-stage boot program.

Risks/notes:
- A commented line says full `p9part(d, "data", 0)` scanning is “not safe yet”.
- Assumes sector sizes compatible with MBR parsing for `mbrpart`.
