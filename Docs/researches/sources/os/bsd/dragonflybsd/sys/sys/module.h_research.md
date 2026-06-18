# File Research: sources/os/bsd/dragonflybsd/sys/sys/module.h

Defines kernel module metadata and module event ABI. Includes metadata types, module event types, `module_t`, event handler type, `moduledata_t`, module-specific stat union, dependency/version/metadata structures, and kernel macros `MODULE_METADATA`, `MODULE_DEPEND`, `DECLARE_MODULE`, and `MODULE_VERSION`.

Kernel APIs register, lookup, reference, release, unload, enumerate, and set module-specific data. User ABI exposes `module_stat`, `modnext`, `modfnext`, `modstat`, and `modfind`. VFS modules use this infrastructure for load/unload and dependency/version metadata.
