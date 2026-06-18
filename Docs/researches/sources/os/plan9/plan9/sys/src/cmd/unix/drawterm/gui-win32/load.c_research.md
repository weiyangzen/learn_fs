# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/load.c

Win32 GUI wrapper exposing `loadmemimage()` as a direct delegation to `_loadmemimage()`.

Role in this group:
- Mirrors the OS X wrapper and keeps public memdraw naming available in the backend.

Notable risks:
- Does not mark or flush a screen region; display refresh depends on callers invoking `flushmemscreen()`.
