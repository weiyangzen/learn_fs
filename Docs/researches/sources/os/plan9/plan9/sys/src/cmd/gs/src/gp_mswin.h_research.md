# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mswin.h

Read status: complete.

Purpose: shared Windows constants and extern declarations for C code and Windows resources.

Contents:
- Resource/control IDs for icons, spool dialog, and cancel dialog states.
- System menu constant `M_COPY_CLIP`.
- Defines `_export` away for Win32 MSVC.
- Declares `phInstance`, `szAppName`, `is_win32s`, and `is_spool`.
- Defines `DLGRETURN` as `INT_PTR` on Win64 and `BOOL` otherwise.

Filesystem/storage relevance:
- Supports Windows printer/spool UI integration but contains no implementation.
