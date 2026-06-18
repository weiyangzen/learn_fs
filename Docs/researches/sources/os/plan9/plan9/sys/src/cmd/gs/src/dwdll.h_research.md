# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwdll.h

Purpose: Declares the Windows Ghostscript DLL dispatch structure and loader API.

Key definitions:
- `GSDLL` stores `HINSTANCE hmodule` plus function pointers for the Ghostscript C API.
- Function pointers cover revision, instance lifecycle, stdio, poll, display callback, argument initialization, string execution, exit, and visual tracing.
- Declares `load_dll(GSDLL *, char *last_error, int len)` and `unload_dll(GSDLL *)`.

Dependencies:
- Requires Windows types and Ghostscript `iapi.h`.
- Forces `__PROTOTYPES__` if absent.

Filesystem relevance: None beyond DLL loading interface.
