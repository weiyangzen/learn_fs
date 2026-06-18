# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs_dll_call.h

Purpose: Defines portable DLL export and calling-convention macros for Ghostscript public APIs.

Key macros: `GSDLLEXPORT`, `GSDLLAPI`, `GSDLLCALL`, `GSDLLAPIPTR`, and `GSDLLCALLPTR`.

Behavior: Windows builds default to `__declspec(dllexport)` and `__stdcall`; OS/2 IBM C builds use `_System`; MacOS enables pragma export; all other platforms default to empty calling-convention/export macros.

Dependencies: Consumed by public headers that must expose stable ABI declarations across Windows, OS/2, MacOS, and generic C platforms.

Risks and notes: Function pointer macro spelling differs for IBM C vs other compilers, which is important for ABI-correct typedefs.
