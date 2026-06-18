# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_module.c

## Purpose

`kern_module.c` implements the kernel module registry layered below the KLD linker. It tracks module names, IDs, containing linker files, reference counts, event handlers, module-private data, and module enumeration/stat syscalls.

## Main Responsibilities

- Initializes the global module list and registers a shutdown event handler.
- Registers modules from `moduledata_t` metadata.
- Calls module event handlers for load, unload, and shutdown.
- Maintains module references and frees modules on final release.
- Looks modules up by name or ID.
- Links modules into both the global module list and the containing linker file's module list.
- Implements `modnext`, `modfnext`, `modstat`, and `modfind` syscalls.

## Data Model

Each `struct module` stores global-list linkage, per-linker-file linkage, containing file pointer, reference count, unique ID, name, event handler, handler argument, and `modspecific_t` data. Module IDs are assigned from `nextid`. The global module list is serialized by `mod_token` for syscall traversal and lookup.

## Lifecycle Behavior

`module_register()` rejects duplicate names, allocates a module plus inline name storage, initializes refs to 1, and links it to the container or `linker_current_file`. `module_register_init()` supports statically initialized modules by registering them against `linker_kernel_file` if necessary, then issuing `MOD_LOAD`; on load failure it unloads and releases the module.

`module_unload()` calls the module's `MOD_UNLOAD` event and lets the handler veto. `module_release()` removes the module from all lists and frees it when its reference count reaches zero. `module_shutdown()` sends `MOD_SHUTDOWN` to every registered module after sync during shutdown.

## Syscall Behavior

`modnext` iterates global module IDs, `modfnext` iterates modules inside a linker file, `modstat` copies name/ref/id and optional module-specific data to userland after checking structure version, and `modfind` resolves a copied-in module name to its ID.
