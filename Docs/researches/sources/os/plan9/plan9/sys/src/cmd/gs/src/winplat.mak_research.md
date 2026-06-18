# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/winplat.mak

Common Windows platform make fragment used by 32-bit Windows and Watcom MS-DOS builds.

Key points:
- Defines `winplat.dev` from `gp_ntfs` and `gp_win32`.
- Compiles `gp_ntfs.c` with DOS/memory/stdio/string/windows and Ghostscript utility headers.
- Compiles `gp_win32.c` with DOS/malloc/stdio/string/windows and Ghostscript platform/memory headers.
- Defines `winsync.dev` from `gp_wsync`, replacing `nosync`.
- Compiles `gp_wsync.c` with Windows and Ghostscript platform/memory headers.

Dependencies and interactions:
- Included by `winlib.mak` and `watclib.mak`.
- Supplies common filesystem/path and synchronization platform modules.

Research relevance:
- The most filesystem-adjacent file in this group: it wires Windows NTFS/path support and Win32 platform/synchronization objects into Ghostscript modules.
