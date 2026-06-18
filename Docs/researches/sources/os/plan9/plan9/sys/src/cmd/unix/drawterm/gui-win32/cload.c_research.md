# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/cload.c

Win32 GUI wrapper for compressed memory-image loading.

Key responsibilities:
- Implements `cloadmemimage()` as a direct call to `_cloadmemimage()`.

Role in this group:
- Complements `load.c` for compressed image data used by drawterm/libdraw paths.

Notable risks:
- No platform-specific update hook is triggered here; callers must flush dirty screen regions separately.
