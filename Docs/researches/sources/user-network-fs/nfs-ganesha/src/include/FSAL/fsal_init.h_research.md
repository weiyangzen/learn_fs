<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_init.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_init.h

## Purpose
`FSAL/fsal_init.h` defines constructor and destructor attribute macros used by FSAL shared modules to register and unregister themselves when dynamically loaded or unloaded.

## Important APIs, types, and functions
- `MODULE_INIT` expands to `__attribute__((constructor))`.
- `MODULE_FINI` expands to `__attribute__((destructor))`.
- Comments document that initializer functions should call `register_fsal` and override default operation vectors, while finalizers must ensure safe unload.

## Control flow
When a FSAL shared object is loaded with `dlopen()`, functions annotated with `MODULE_INIT` run before `dlopen()` returns. On unload, functions annotated with `MODULE_FINI` run to release module-level resources after the core has verified unload safety.

## State and persistence
The macros do not define state. They control module lifecycle hooks that initialize and tear down process-local FSAL module state.

## Dependencies and integration points
The header depends on compiler support for GNU constructor/destructor attributes. It integrates FSAL modules with the dynamic module loader and Ganesha's `register_fsal` flow.

## Risks
- Constructors/destructors are compiler- and platform-specific; non-GNU toolchains may need alternate definitions.
- Constructor order across multiple modules is not generally controllable beyond dynamic load order.
- Finalizers must not run while exports or object handles still reference the module; the comment calls out this invariant but enforcement lives elsewhere.

## Test signals
- Build tests should compile FSAL modules on every supported compiler/platform.
- Dynamic loading tests should verify module registration occurs before use and finalizers run only after safe unload.
- Failure tests should cover constructor registration errors and module unload refusal with active references.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_init.h -->
