## sources/test-tools/filebench/fb_cvar.h

### Purpose
`fb_cvar.h` defines the ABI between Filebench and custom variable shared libraries, plus the runtime structures Filebench uses to track those libraries and variable handles.

### Important APIs, Types, And Functions
Symbol-name macros identify plugin functions: `cvar_module_init`, `cvar_alloc_handle`, `cvar_revalidate_handle`, `cvar_next_value`, `cvar_free_handle`, `cvar_module_exit`, `cvar_usage`, and `cvar_version`. `cvar_library_info_t` stores shared metadata (`filename`, `type`, `index`, `next`). `cvar_t` stores a mutex, plugin handle, bounds, rounding, library info pointer, and list link. `cvar_operations_t` is the dlsym-populated function vector. `cvar_library_t` pairs metadata with a `dlopen` handle and operations vector. The header declares all cvar runtime functions and `cvar_libraries`.

### Control Flow
The declared model is discovery first, library initialization second, handle initialization per cvar third, then repeated value generation through the bound `cvar_next_value` function. Revalidation can be run later across all handles.

### State And Persistence
The structures distinguish shared metadata and handles from process-local library handles. The `cvar_t` mutex is intended for exclusive access across threads and processes. Bounds and rounding are stored directly on each cvar object and enforced by `get_cvar_value`.

### Dependencies And Integration Points
It includes integer and system types and requires pthread types through the wider Filebench include environment. It is included by Filebench runtime code and external cvar sanity tests.

### Risks
The ABI uses raw function pointers and `void *` handles, so type safety is entirely conventional. Plugin allocation/free functions must use the allocator callbacks provided by Filebench. Optional hooks are nullable; callers must check before invoking. The header does not encode ownership for strings and handles, which is handled by implementation convention.

### Test Signals
Compile-time tests should build a minimal plugin exporting required symbols. Runtime tests should load that plugin, allocate a handle, generate values, revalidate, free, and verify optional version/usage/module hooks.
