# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/sysuse.c

Rock Ridge/SUSP system-use record writer for ISO directory entries.

Key behavior:
- Computes and writes SUSP/RRIP records including `SP`, `ER`, `RR`, `PX`, `NM`, `SL`, `TF`, and continuation `CE`.
- `Cputsysuse` first sizes and then writes records, managing inline directory-entry space and continuation blocklets.
- Long names and symlink components are split across NM/SL records as needed.
- Continuation areas are block-aligned and linked with CE records whose length fields are patched after writing.
- POSIX mode, nlink, uid/gid, and timestamps are derived from `Direc`.

Notable dependencies:
- `Cputn`, `Cputdate`, `Cwoffset`, `Cwseek`, `chat`.
- Plan 9 mode bits and optional `CHLINK` symlink flag.

Research notes:
- The implementation explicitly calls the format awkward and is full of defensive asserts around continuation sizing.
- `mode` asserts only directory or regular-file support despite defining symlink constants, which may conflict with `CHLINK` symlink handling.
