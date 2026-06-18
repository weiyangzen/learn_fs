# sources/test-tools/stress-ng/core-module.c

Purpose: wraps Linux kernel module load/unload behavior for module stressors, with stubs on unsupported platforms.

Important APIs/functions: `stress_module_load`, `stress_module_unload`, and internal `stress_module_unload_mod_and_deps`. On libkmod/Linux builds it uses lookup, probe/insert, dependency traversal, refcount checks, and module removal.

Control flow: load creates a kmod context, resolves an alias to module list entries, then probes/inserts each module. `EEXIST` is success with `already_loaded=true`. Unload exits early for modules that preexisted, skips built-ins, logs busy modules, and recursively removes dependency modules with zero refcount.

State/persistence: affects persistent kernel module state by loading/removing modules. Tracks only caller-provided `already_loaded` process state.

Dependencies/integration: included by module stressor code; depends on `core-module.h`, `stress-ng.h`, libkmod headers/library, Linux, logging helpers, and build feature macros.

Risks: module operations require privileges and can affect the running kernel. Dependency unload can race other users even with refcount checks. Unsupported builds return `-1`, so callers must tolerate absence.

Test signals: libkmod and stub builds, already-loaded modules, load failure paths, no-unload cleanup, built-in module lookup, dependency refcount behavior, and unprivileged execution.
