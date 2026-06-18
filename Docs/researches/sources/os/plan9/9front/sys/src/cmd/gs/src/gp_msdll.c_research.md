# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_msdll.c

Windows DLL entry point support.

Key behavior:
- Defines `DllEntryPoint` for Borland C++ and `DllMain` for Microsoft Visual C++.
- Records the DLL instance handle in `phInstance`.
- Detects Win32s by inspecting `GetVersion` high-word bits and sets `is_win32s`.

Notable dependencies:
- Windows headers and shared declarations from `gp_mswin.h`.
- Export macros from `iapi.h`.

Research notes:
- This file only initializes global DLL platform state; it does not implement I/O itself.
