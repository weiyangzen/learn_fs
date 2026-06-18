# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/load.c

Tiny OS X GUI wrapper exposing the public `loadmemimage()` name while delegating directly to libmemdraw’s underscored `_loadmemimage()`.

Key responsibilities:
- Includes Plan 9 compatibility headers and draw/memdraw interfaces.
- Implements `loadmemimage(Memimage *i, Rectangle r, uchar *data, int ndata)` as a pass-through.

Role in this group:
- Keeps the OS X backend ABI consistent with other drawterm GUI backends while allowing platform files to interpose selected memdraw routines.

Notable risks:
- No validation or synchronization is performed here; callers rely entirely on `_loadmemimage()` and surrounding draw locks.
