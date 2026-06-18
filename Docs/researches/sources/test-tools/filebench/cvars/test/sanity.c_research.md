## sources/test-tools/filebench/cvars/test/sanity.c

### Purpose
`sanity.c` is a standalone dynamic-loader sanity checker for Filebench custom variable libraries. It loads a cvar shared object, resolves the expected symbol vector, allocates a custom-variable handle from a parameter string, revalidates it, prints requested generated values, and frees the handle.

### Important APIs, Types, And Functions
`main` is the only runtime entry point. It uses `cvar_operations_t` from `fb_cvar.h` and the symbol-name macros `FB_CVAR_MODULE_INIT`, `FB_CVAR_ALLOC_HANDLE`, `FB_CVAR_REVALIDATE_HANDLE`, `FB_CVAR_NEXT_VALUE`, `FB_CVAR_FREE_HANDLE`, `FB_CVAR_MODULE_EXIT`, `FB_CVAR_USAGE`, and `FB_CVAR_VERSION`. `print_usage()` explains the shared-library, parameter-string, and count arguments.

### Control Flow
The program validates three user arguments, opens the library with `dlopen(..., RTLD_NOW | RTLD_GLOBAL)`, resolves required and optional symbols with `dlsym`, calls optional module init/version/usage hooks, then calls `cvar_alloc_handle(parameters, malloc, free)`. It revalidates the handle, loops `count` times calling `cvar_next_value`, prints comma-separated values, frees the handle, calls optional module exit, closes the library, and returns an error-specific status on failure paths.

### State And Persistence
State is local to the process: a `dlopen` handle, a module-created `cvar_handle`, and transient generated values. No Filebench shared memory is used despite including the same cvar ABI. No persistent output beyond stdout/stderr is produced.

### Dependencies And Integration Points
It depends on `dlfcn.h`, libc allocation functions, and `fb_cvar.h`. It is an external contract checker for cvar modules built under `sources/test-tools/filebench/cvars`.

### Risks
The cleanup path always calls `cvar_free_handle(cvar_handle, free)` at label `cvar_free`; if allocation failed and `cvar_handle` was not initialized, this can pass an indeterminate pointer. Some error messages reference the wrong symbol macro in the revalidate failure branch. `atoi` silently accepts invalid counts. Using `RTLD_GLOBAL` can mask symbol-collision issues or be required by some modules, depending on plugin design.

### Test Signals
A successful run prints the variable name/version, optional usage, generated values, and `All done.` with exit code zero. Negative tests should cover missing symbols, failing `cvar_module_init`, invalid parameter strings, allocation failure, revalidation failure, and zero/negative count behavior.
