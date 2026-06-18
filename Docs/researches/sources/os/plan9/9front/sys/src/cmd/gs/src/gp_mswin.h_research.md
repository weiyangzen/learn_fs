# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mswin.h

Shared Windows platform/resource header.

Key contents:
- Defines resource/control IDs for Ghostscript text/image icons, spool dialog controls, and cancel controls.
- Defines image-window system-menu command `M_COPY_CLIP`.
- Handles `_export` compatibility for 32-bit MSVC.
- Declares `phInstance`, `szAppName`, `is_win32s`, and `is_spool`.
- Defines `DLGRETURN` as `INT_PTR` on Win64 and `BOOL` otherwise.

Research notes:
- The header is designed for use by both C code and Windows resource scripts, so declarations are hidden under `!RC_INVOKED`.
