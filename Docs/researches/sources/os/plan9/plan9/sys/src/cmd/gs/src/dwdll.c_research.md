# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwdll.c

Purpose: Runtime loader for `gsdll32.dll` on Windows.

Key behavior:
- `load_dll` tries to load `gsdll32.dll` from:
  1. The executable directory.
  2. `GS_DLL` environment/registry value via `gp_getenv`.
  3. The system DLL search path.
- After loading, it resolves Ghostscript API entry points with `GetProcAddress`.
- Validates DLL revision using `gsapi_revision` against compiled `gs_revision`.
- Required functions include instance creation/deletion, stdio, poll, display callback, initialization, run-string, exit, and visual tracer setup.
- `unload_dll` nulls all function pointers and frees the module.

Risks/legacy notes:
- Uses fixed 1024-byte path buffer and `strcat`/`sprintf`.
- Uses old `HINSTANCE_ERROR` comparison style.
- Does not consistently force NUL termination after `strncpy`.

Filesystem relevance: DLL discovery path behavior only.
