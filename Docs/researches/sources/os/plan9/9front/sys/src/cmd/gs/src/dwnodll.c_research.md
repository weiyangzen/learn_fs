# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwnodll.c

## Role
Static-link alternative to `dwdll.c` for filling the `GSDLL` table without loading a DLL.

## Contents
- Includes the same Ghostscript/Win32 setup headers as the dynamic loader.
- `load_dll` assigns Ghostscript API function pointers directly to linked symbols.
- `unload_dll` is a no-op.

## Important Interfaces
- `load_dll`.
- `unload_dll`.

## Dependencies And Coupling
- Requires the Ghostscript API symbols (`gsapi_new_instance`, `gsapi_delete_instance`, etc.) to be linked into the executable.
- Uses the same `GSDLL` structure as dynamic loading.

## Risks And Notes
- Does not populate `revision` or `hmodule`; consumers relying on those fields after load must account for static mode.
- No version check is performed because the functions are statically linked.

## Filesystem Relevance
None.
