# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_module.c

Read completely: 569 lines.

## Purpose
Implements the kernel module registry: module registration, load/unload/quiesce/shutdown event dispatch, reference counting, per-linker-file module ordering, and userland module enumeration/stat syscalls.

## Main Elements
- `struct module` stores global/file list links, owning linker file, reference count, numeric ID, name, event handler, private arg, and module-specific data.
- `module_init()` initializes `modules_sx`, the global module list, and shutdown event handling.
- `module_shutdown()` walks modules in reverse order and sends `MOD_SHUTDOWN`.
- `module_register()` allocates and inserts a module, assigns a unique ID, checks for duplicate names, and links into the containing linker file.
- `module_register_init()` locates the module, invokes `MOD_LOAD`, unwinds on failure, and reorders file-local modules so unload happens in reverse load order.
- `module_reference()` and `module_release()` manage references and free zero-ref modules.
- Lookup/accessor helpers expose module lookup by name/id, next-in-file, name, ID, specific data, and owning linker file.
- `module_quiesce()` and `module_unload()` dispatch module events under Giant.
- Syscalls `modnext`, `modfnext`, `modstat`, and `modfind` enumerate and inspect loaded modules.
- Compatibility code supports 32-bit `modstat` layout and older v1/v2 structure sizes.
- Declares `MODULE_VERSION(kernel, __FreeBSD_version)`.

## Dependencies And Integration
Uses linker files, KLD startup ordering, sx locks through `MOD_*LOCK` macros, Giant around module event handlers, syscalls/copyin/copyout, shutdown eventhandlers, malloc type `M_MODULE`, and FreeBSD32 compatibility.

## Risk Notes
Module data is copied out after snapshotting under the shared lock, but name pointers are still derived from module state, so lifetime depends on module lock/ref discipline. Event handlers run under Giant, preserving older module assumptions. Duplicate module names are rejected globally, even across different linker files.
