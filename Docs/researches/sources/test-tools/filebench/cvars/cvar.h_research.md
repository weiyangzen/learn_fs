<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar.h -->
# `sources/test-tools/filebench/cvars/cvar.h`

Purpose: ABI contract between Filebench and dynamically loaded custom-variable modules.

Important APIs: declares optional `cvar_module_init`, `cvar_revalidate_handle`, `cvar_module_exit`, `cvar_usage`, `cvar_version`; mandatory `cvar_alloc_handle`, `cvar_next_value`, and `cvar_free_handle`.

Control flow: Filebench loads a module, optionally initializes it, allocates a handle using Filebench-provided allocation callbacks, revalidates handles that were created in a different process, repeatedly calls `cvar_next_value`, and may call free/exit during teardown.

State and persistence: module handles are allocated with caller-provided memory functions, likely so Filebench can place them in shared memory. Modules must not retain allocator callback pointers.

Dependencies and integration: all CVAR modules include this header and export these exact symbol names for dynamic lookup.

Risks: function prototypes omit `void` in empty parameter lists, which is old-style C and weaker under strict compilers. Lifecycle comments explicitly allow Filebench to skip cleanup callbacks, so modules must tolerate process-exit cleanup. ABI is symbol-name based with no versioned struct.

Test signals: dynamic-loader tests should verify missing optional symbols are tolerated and missing mandatory symbols fail clearly; shared-memory revalidation should be exercised.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar.h -->
