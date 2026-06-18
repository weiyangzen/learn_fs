# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_msdll.c

Read status: complete.

Purpose: Microsoft Windows DLL entry-point support for Ghostscript.

Main logic:
- `DllEntryPoint` checks `GetVersion` bits to detect Win32s and sets global `is_win32s`.
- Stores the DLL instance handle in global `phInstance`.
- `DllMain` delegates to `DllEntryPoint`.

Filesystem/storage relevance:
- None directly. The instance handle is used by Windows UI/resource code such as printer dialogs.

Notable behavior:
- Provides both Borland-style and Microsoft Visual C++ DLL entry points.
