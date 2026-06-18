# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/vfs_only.cmake

Purpose: Minimal VFS-focused preset with DBus enabled and several non-VFS features disabled.

Important APIs/types/functions: Disables `USE_FSAL_PROXY_V4`, `USE_FSAL_CEPH`, `USE_FSAL_GPFS`, `_MSPAC_SUPPORT`, and `USE_9P`; enables `USE_DBUS`.

Control flow: Included during configure to shape later option/dependency decisions.

State and persistence behavior: CMake configuration state only.

Dependencies and integration points: Keeps the build near VFS plus DBus, reducing optional FSAL dependency discovery.

Risks: As with other presets, future FSALs not explicitly disabled may still be enabled by defaults. DBus remains enabled despite the "vfs only" name, so a truly minimal build may require additional overrides.

Test signals: Configure and verify only expected VFS/DBus targets are built; run with missing Ceph/GPFS deps to ensure they are not required.
