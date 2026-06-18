# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwdll.h

## Role
Header defining the Win32 Ghostscript DLL function table and loader API.

## Contents
- Ensures `__PROTOTYPES__` is defined before including `iapi.h`.
- Defines `GSDLL` with an `HINSTANCE` module handle and function pointers for revision, instance lifecycle, stdio, polling, display callback, initialization, string execution, exit, and visual tracer APIs.
- Declares `load_dll` and `unload_dll`.

## Important Interfaces
- `GSDLL` struct.
- `load_dll`/`unload_dll`.

## Dependencies And Coupling
- Requires Windows `HINSTANCE` to be available before use.
- Depends on Ghostscript API pointer typedefs from `iapi.h`.

## Risks And Notes
- Consumers must check loader success before using function pointers.
- Header supports both dynamic (`dwdll.c`) and static (`dwnodll.c`) binding implementations.

## Filesystem Relevance
No direct filesystem behavior.
