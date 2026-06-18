# sources/test-tools/crashmonkey/code/utils/ClassLoader.h

Purpose: header-only template for dynamically loading test-case classes from shared libraries. CrashMonkey uses this to load workload `.so` files exposing factory and deleter symbols.

Important APIs/types/functions: template `ClassLoader<T>`, `load_class<F>`, `unload_class<DF>`, `get_instance`, `dlopen`, `dlsym`, `dlclose`, and status macros `SUCCESS`, `CASE_HANDLE_ERR`, `CASE_INIT_ERR`, `CASE_DEST_ERR`.

Control flow: `load_class` opens a shared object, resolves factory and defactory symbols, creates an instance through the typed factory function pointer, and stores handles. `unload_class` calls the typed deleter and closes the handle if both handle and instance exist.

State/persistence behavior: maintains in-process dynamic loader state: library handle, function pointers, and one live object pointer. No persistent filesystem state is changed after loading.

Dependencies/integration: depends on `libdl` and test shared libraries exporting matching names. Risks/test signals: type safety is caller-enforced via template casts, error paths print to `stderr`, symbol names are stringly typed, and a factory returning null is not treated as load failure.
