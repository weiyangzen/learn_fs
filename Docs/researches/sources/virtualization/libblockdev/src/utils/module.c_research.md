# File Research: sources/virtualization/libblockdev/src/utils/module.c

Implementation of libblockdev utility helpers for Linux kernel module discovery/loading/unloading and cached running-kernel version detection.

Key responsibilities:
- Defines `bd_utils_module_error_quark()` for the GLib error domain used by module and kernel-version helpers.
- Bridges libkmod logging into libblockdev logging through `utils_kmod_log_redirect()` and `set_kmod_logging()`, using `LOG_DEBUG` in debug builds and `LOG_INFO` otherwise.
- Implements `bd_utils_have_kernel_module()`, which uses `kmod_module_new_from_lookup()` so aliases are considered, then treats a module as available if it has a filesystem path or is reported as `KMOD_MODULE_BUILTIN`.
- Implements `bd_utils_load_kernel_module()`, which resolves a module by name, rejects missing module paths with `BD_UTILS_MODULE_ERROR_NOEXIST`, then calls `kmod_module_probe_insert_module()` with `KMOD_PROBE_FAIL_ON_LOADED`.
- Implements `bd_utils_unload_kernel_module()`, which enumerates loaded modules, finds an exact module-name match, and calls `kmod_module_remove_module()`.
- Implements `bd_utils_get_linux_version()` and `bd_utils_check_linux_version()` around a process-global cached `BDUtilsLinuxVersion` populated from `uname(2)`.

Dependencies and integration:
- Depends on GLib, libkmod, syslog priority constants, POSIX locale APIs, and `uname(2)`.
- Includes local `module.h`, `exec.h`, and `logging.h`; only `module.h` supplies the public declarations used here.
- Built into `libbd_utils.la` by `src/utils/Makefile.am` and linked with `$(KMOD_LIBS)`.
- The main in-tree caller of `bd_utils_have_kernel_module()` is `src/plugins/check_deps.c`, where failed checks are folded into plugin dependency availability bitmaps.
- Exported API symbols are listed in `docs/libblockdev-sections.txt`.

Implementation notes:
- Kmod contexts are created with a null config pointer array, so these helpers avoid loading libkmod configuration snippets from an explicit caller-supplied configuration.
- Error text uses `strerror_l()` with a freshly created C locale to make system error strings locale-stable.
- `bd_utils_have_kernel_module()` returns `FALSE` with no `GError` when lookup succeeds but yields no module list; callers distinguish this from operational lookup failures.
- The load helper treats already-loaded modules as a failure because `KMOD_PROBE_FAIL_ON_LOADED` is intentionally used for backward-compatible behavior.
- The unload helper only attempts removal after finding the module among currently loaded modules; an unloaded or unknown module produces `BD_UTILS_MODULE_ERROR_NOEXIST`.
- Linux version detection validates `buf.sysname` against `Linux`, parses up to `major.minor.micro` from `buf.release`, and leaves missing minor/micro components as zero because the cached struct is zeroed before `sscanf()`.
- `bd_utils_check_linux_version()` serializes access with `G_LOCK`, lazily initializes the cache if needed, and returns the first nonzero difference among major, minor, and micro.

Notable risks:
- The kmod log prefix is spelled `[libmkod]`, which looks like a typo but may be visible in logs.
- `newlocale()` return values are not checked before use with `strerror_l()`; allocation failure would make error formatting fragile.
- `bd_utils_check_linux_version()` ignores initialization failure because it calls `_get_linux_version(FALSE, NULL)` and then compares the zeroed cached struct if detection failed.
- The module loading path rejects modules without a module file path, so built-in modules are "available" to `bd_utils_have_kernel_module()` but not loadable through `bd_utils_load_kernel_module()`.
