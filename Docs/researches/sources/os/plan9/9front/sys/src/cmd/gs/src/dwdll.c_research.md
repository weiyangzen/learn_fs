# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwdll.c

## Role
Win32 dynamic loader for the Ghostscript DLL (`gsdll32.dll`), populating a `GSDLL` function table.

## Contents
- Tries to load the DLL from the executable directory, then from the `GS_DLL` registry/environment value via `gp_getenv`, then via the system search path.
- Reports `LoadLibrary` failures through caller-provided `last_error`.
- Resolves Ghostscript API entry points with `GetProcAddress`.
- Checks `gsapi_revision` and requires the DLL revision to equal the compile-time `gs_revision`.
- On any missing symbol or version mismatch, unloads the DLL and returns failure.
- `unload_dll` clears all function pointers and calls `FreeLibrary`.

## Important Interfaces
- `int load_dll(GSDLL *gsdll, char *last_error, int len)`.
- `void unload_dll(GSDLL *gsdll)`.

## Dependencies And Coupling
- Includes Windows API, `gpgetenv.h`, `gscdefs.h`, and `dwdll.h`.
- Depends on symbols declared by `iapi.h` through `dwdll.h`.
- Hard-codes `gsdll32.dll` and revision equality.

## Risks And Notes
- Uses fixed-size buffers and `strcat`/`sprintf`; safe only if executable paths remain under the 1024-byte buffer size.
- Uses old `HINSTANCE_ERROR` comparison idiom.
- `strncpy(last_error, ..., len-1)` does not explicitly append a NUL after truncation.

## Filesystem Relevance
Loads DLLs from filesystem paths and search paths; no filesystem implementation.
