# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/iso_rrip.h

Read completely: 87 lines.

Purpose: declares Rock Ridge Interchange Protocol analysis flags, the RRIP analysis context, and kernel RRIP helper APIs for cd9660.

Key definitions:
- `ISO_SUSP_*` bit flags identify SUSP/RRIP fields such as attributes, device numbers, symbolic links, alternate names, child/parent links, relocated directories, timestamps, continuation areas, offsets, stop records, and unknown records.
- `ISO_RRIP_ANALYZE` carries state for RRIP analysis: target `iso_node`, requested fields, continuation area location/length, mount, inode pointer, output buffer/length, max length, and continuation status.

Exported kernel APIs:
- `cd9660_rrip_analyze()` fills an `iso_node` from RRIP fields.
- `cd9660_rrip_getname()` extracts alternate names and inode updates for readdir.
- `cd9660_rrip_getsymname()` extracts symlink targets.
- `cd9660_rrip_offset()` detects SUSP/RRIP offset for a directory record.

Research notes:
- This is only the interface; implementation lives elsewhere.
- The VFS and vnode files rely on this header to switch cd9660 from plain ISO semantics to Unix-like RRIP metadata.
