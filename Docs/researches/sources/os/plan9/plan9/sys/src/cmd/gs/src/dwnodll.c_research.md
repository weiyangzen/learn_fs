# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwnodll.c

Purpose: Static-link alternative to `dwdll.c`.

Behavior:
- `load_dll` does not load a DLL. It assigns `GSDLL` function pointers directly to linked `gsapi_*` symbols.
- `unload_dll` is a no-op.

Use case:
- Allows the same Windows main programs to call through the `GSDLL` dispatch table whether Ghostscript is loaded dynamically or statically linked.

Filesystem relevance: None.
