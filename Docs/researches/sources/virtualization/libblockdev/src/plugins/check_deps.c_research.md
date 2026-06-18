# File Research: sources/virtualization/libblockdev/src/plugins/check_deps.c

## Role
Shared dependency checker used by multiple libblockdev plugins. It caches runtime availability of command-line utilities, kernel modules, D-Bus services/API versions, and utility feature support.

## Utility Version Dependencies
- `check_deps()` accepts an atomic availability bitmask, requested dependency bits, an array of `UtilDep`, dependency count, a lock, and error output.
- It returns immediately if all requested bits are already cached.
- Otherwise it serializes checks with `deps_check_lock`, rechecks the cache, then calls `bd_utils_check_util_version()`.
- Successful checks set the matching bit with `g_atomic_int_or()`.
- Failures are accumulated into `GError`, prefixing existing errors when multiple checks fail.

## Kernel Module Dependencies
- `check_module_deps()` follows the same cache/lock pattern.
- Calls `bd_utils_have_kernel_module()` per requested module.
- Distinguishes helper errors from simple unavailable modules, producing `BD_UTILS_MODULE_ERROR_MODULE_CHECK_ERROR`.

## D-Bus Dependencies
- `_check_dbus_api_version()` connects to the specified bus, calls `org.freedesktop.DBus.Properties.Get`, extracts a version string, and compares it with `bd_utils_version_cmp()`.
- `check_dbus_deps()` first checks service availability via `bd_utils_dbus_service_available()`.
- If a version is configured, it also verifies the D-Bus API version before caching the dependency bit.
- Errors cover missing service, service-check failures, and insufficient API version.

## Utility Feature Dependencies
- `_check_util_feature()` locates the utility in `PATH`, runs it with a feature argument, and captures output.
- If the command returns no stdout or nonzero exit status, it can still inspect the error message text as output.
- Optional regex extraction can narrow output to a feature list.
- Checks feature availability with substring search.
- `check_features()` wraps this in the same atomic cache and lock pattern used by other dependency checks.

## Concurrency and Caching
- All public check functions are designed for repeated plugin calls.
- Atomic bitmasks avoid repeated external process/module/D-Bus checks once a dependency has been confirmed.
- Mutexes prevent concurrent duplicate checks when dependencies are not yet cached.

## Filesystem/Storage Relevance
Filesystem and block plugins use this file to gate operations on real runtime capabilities. For Btrfs specifically, `btrfs.c` uses it to require btrfs-progs versions and the Btrfs kernel module before running mutating or query operations.
