# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/draw.c

Win32 GUI wrapper for selected libmemdraw drawing routines.

Key responsibilities:
- Implements `memimagedraw()` by calling `_memimagedrawsetup()` then `_memimagedraw()`.
- Exposes `pixelbits()` through `_pixelbits()`.
- Exposes `memimageinit()` through `_memimageinit()`.

Role in this group:
- Provides unaccelerated in-memory draw operations for the Win32 backend.

Notable risks:
- Assumes `_memimagedrawsetup()` succeeds; unlike some wrappers, it does not check for nil before passing into `_memimagedraw()`.
