# Research: sources/storage-engines/wiredtiger/test/catch2/utils.h

## sources/storage-engines/wiredtiger/test/catch2/utils.h

Purpose: Shared utility declarations and a small RAII wrapper for dynamic libraries.

Important APIs/types: defines `DB_HOME` as `test_db`, `BREAK` macro, functions `break_here`, `throw_if_non_zero`, `wiredtiger_cleanup`, and class `utils::shared_library`.

Control flow: `shared_library` constructor opens a library with `__wt_dlopen`, destructor closes it with `__wt_dlclose`, copy operations are deleted, and templated `get` resolves a symbol with `__wt_dlsym`, throwing on failure through `throw_if_non_zero`.

State and persistence: `shared_library` owns a `WT_DLH *` handle for the object's lifetime. Other utilities manage cleanup externally.

Dependencies/integration: included by C++ wrappers and tests, depends on `wt_internal.h` dynamic loading abstractions. Risks include using `nullptr` session with dlopen/dlclose and process-global dynamic loader behavior. Test signals are exceptions from failed WT dynamic-loader calls and breakpoint info through Catch2.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/utils.h -->
