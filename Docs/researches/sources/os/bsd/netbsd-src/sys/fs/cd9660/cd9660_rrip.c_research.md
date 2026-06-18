# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_rrip.c

Read completely: 709 lines.

Implements Rock Ridge Interchange Protocol support for NetBSD cd9660. The file is table-driven around `RRIP_TABLE` entries that map SUSP/RRIP field signatures (`PX`, `TF`, `PN`, `NM`, `SL`, `CL`, `PL`, `RE`, `RR`, `CE`, `ST`, `ER`) to parser callbacks and optional defaults.

`cd9660_rrip_loop()` is the core scanner. It computes the System Use area after the ISO directory name, applies root/non-root skip offsets, walks SUSP records, follows continuation areas through `CE`, bounds-checks continuation block/offset/length against volume size and logical block size, and calls default handlers for missing required attributes or timestamps.

The public entry points separate RRIP tasks: `cd9660_rrip_analyze()` fills inode mode, uid, gid, link count, device number, and timestamps; `cd9660_rrip_getname()` builds alternate names and handles relocated directories/child-parent links; `cd9660_rrip_getsymname()` assembles symbolic link components with current, parent, root, volume-root, host, and continuation semantics; `cd9660_rrip_offset()` validates `SP` and `ER` records before enabling Rock Ridge.

Important edge handling includes fallback to ISO names/timestamps when RRIP fields are absent, overflow protection for alternate names and symlink buffers, rejection of too-short `NM` entries, SUSP stop handling, and CD-ROM XA skip handling for `SP`.
