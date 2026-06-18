# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/winplat.mak

Common 32-bit Windows platform module makefile fragment.

Key points:
- Defines generic Windows platform module `winplat.dev` from `gp_ntfs` and `gp_win32`.
- Compiles `gp_ntfs.c` and `gp_win32.c` with Windows include dependencies.
- Defines synchronization module `winsync.dev` from `gp_wsync`.
- `winsync.dev` replaces `nosync` in the generated module list.

Dependencies and interactions:
- Included by `winlib.mak` and `watclib.mak`.
- Supplies platform and synchronization modules to Windows and Watcom builds.

Research relevance:
- Minimal Windows OS abstraction and synchronization build wiring.
