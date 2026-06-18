## sources/test-tools/filebench/fb_cvar.c

### Purpose
`fb_cvar.c` implements Filebench custom variable support. It discovers cvar shared libraries, records their metadata in shared memory, loads each library per process, binds required function symbols, allocates per-variable handles, retrieves values, clamps/rounds them, and revalidates handles.

### Important APIs, Types, And Functions
Public functions are `cvar_alloc`, `init_cvar_library_info`, `init_cvar_libraries`, `init_cvar_handle`, `get_cvar_value`, and `revalidate_cvar_handles`. Internal helpers include `alloc_cvar_lib_info`, `gettype`, `init_cvar_library`, `load_library`, `free_cvar_library`, and `init_cvar_library_ops`. The global `cvar_libraries` points to the per-process array of loaded library objects.

### Control Flow
Discovery scans a directory for names ending in `.so`, derives a type by stripping leading `lib` and suffix after the first dot, and appends `cvar_library_info_t` records to `filebench_shm`. Initialization counts those records, allocates an array, loads each shared object with `dlopen`, resolves required and optional symbols, and invokes optional module init. Handle initialization finds a matching type and calls the plugin's `cvar_alloc_handle`. Value retrieval locks the cvar, calls `cvar_next_value`, unlocks, rounds to nearest configured increment, and clamps to min/max.

### State And Persistence
Library metadata is shared-memory state (`shm_cvar_lib_info_list`) so child processes can find the same library types. Actual `dlopen` handles and function vectors are process-local in `cvar_libraries`. Individual `cvar_t` objects live in shared memory and carry a cross-process mutex, bounds, round value, plugin handle, and library info pointer.

### Dependencies And Integration Points
It depends on `ipc.h`, `fb_cvar.h`, directory iteration, `dlfcn`, and Filebench logging/shutdown. Parser code creates cvars and variables can call `get_cvar_value` through the variable subsystem. The module ABI is tested externally by `cvars/test/sanity.c`.

### Risks
`gettype` allocates a temporary type string that is copied into IPC memory but never freed by `alloc_cvar_lib_info`. Error cleanup notes that `cli->filename` and `cli->type` cannot be freed. `init_cvar_libraries` does not unwind already loaded libraries on later failure. Missing `cvar_revalidate_handle` is logged but not fatal despite being part of the named operation set. The array `cvar_libraries` has no stored count, so callers rely on shared metadata indexes remaining consistent.

### Test Signals
Tests should cover directory discovery, type derivation, loading libraries with required/optional symbols, module init failure, handle allocation failure, value rounding/clamping, concurrent `get_cvar_value`, and revalidation across all configured handles.
