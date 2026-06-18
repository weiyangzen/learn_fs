# File Research: sources/virtualization/libblockdev/src/utils/module.h

Public libblockdev utility header for kernel module helper errors, module management entry points, and Linux kernel version comparison.

Key responsibilities:
- Declares `bd_utils_module_error_quark()` and the `BD_UTILS_MODULE_ERROR` domain macro.
- Defines `BDUtilsModuleError` values for kmod initialization failure, generic module operation failure, missing module state, dependency-check aggregation failure, and invalid platform.
- Defines `BDUtilsLinuxVersion` as a simple `guint` triplet of major, minor, and micro kernel release components.
- Declares public helpers to check for a module, load a module with optional options, unload a module, get the cached Linux version, and compare the running kernel against a minimum version.

Dependencies and integration:
- Includes GLib for `GQuark`, `gboolean`, `gchar`, `GError`, `guint`, and `gint`.
- Installed as a public header by `src/utils/Makefile.am` under `$(includedir)/blockdev`.
- Included by the umbrella `src/utils/utils.h`, making this API visible to consumers that include `<blockdev/utils.h>`.
- Its symbols are documented/exported through `docs/libblockdev-sections.txt`.

Notable risks:
- `BD_UTILS_MODULE_ERROR_MODULE_CHECK_ERROR` is not raised by `module.c` directly; it is used by higher-level dependency checking in `src/plugins/check_deps.c`, so consumers need to treat the enum as shared across utility and plugin dependency layers.
- `BDUtilsLinuxVersion *` returned by the implementation is library-owned static storage; callers must not free or mutate it even though the struct type itself is not const-qualified in the API.
