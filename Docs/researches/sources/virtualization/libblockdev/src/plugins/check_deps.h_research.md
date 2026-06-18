# File Research: sources/virtualization/libblockdev/src/plugins/check_deps.h

## Role
Internal shared header for plugin runtime dependency checks.

## Data Structures
- `UtilDep`: utility name, required version, optional version argument, and version regex.
- `DBusDep`: bus name, object prefix, bus type, required version, and property/interface/path fields for version probing.
- `UtilFeatureDep`: utility name, required feature, feature argument, and optional feature regex.

## API
Declares four checker functions:
- `check_deps()` for utility/version dependencies;
- `check_module_deps()` for kernel modules;
- `check_dbus_deps()` for D-Bus service and API dependencies;
- `check_features()` for utility feature discovery.

Each function accepts an atomic availability bitmask, requested dependency bits, dependency specs, dependency count, a mutex, and optional `GError`.

## Dependencies and Interactions
- Used by `btrfs.c` and other plugin implementations listed in `src/plugins/Makefile.am`.
- Implemented by `check_deps.c`.
- Depends on GLib types and libblockdev utility helpers indirectly through the C implementation.

## Filesystem/Storage Relevance
This header defines the reusable runtime-gating interface that keeps plugin operations from running when required tools, modules, services, or features are unavailable.
