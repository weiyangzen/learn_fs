# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/alloc.c

Win32 GUI wrapper for memory-image allocation helpers.

Key responsibilities:
- Exposes `allocmemimage`, `freememimage`, and `memfillcolor`.
- Delegates directly to `_allocmemimage`, `_freememimage`, and `_memfillcolor`.

Role in this group:
- Provides public memdraw names for the Win32 GUI backend without the X11 pixmap interposition layer.

Notable risks:
- No Windows-specific acceleration or GDI synchronization occurs here; screen updates depend on explicit `screenload()` calls in `screen.c`.
