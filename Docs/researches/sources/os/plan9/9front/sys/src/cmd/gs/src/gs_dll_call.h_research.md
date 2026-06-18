# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gs_dll_call.h

Purpose: Calling-convention macros for Ghostscript DLL APIs.

Platform behavior: On Windows, defines `GSDLLEXPORT` as `__declspec(dllexport)` and `GSDLLAPI`/`GSDLLCALL` as `__stdcall` unless already defined. On IBM C for OS/2, maps calling conventions to `_System`. On Mac OS, enables export pragmas.

Pointer macros: Defines `GSDLLAPIPTR` and `GSDLLCALLPTR` with compiler-specific placement of calling-convention attributes around function pointers.

Dependencies and notes: Falls back to empty macros on unsupported platforms, keeping public headers portable.
