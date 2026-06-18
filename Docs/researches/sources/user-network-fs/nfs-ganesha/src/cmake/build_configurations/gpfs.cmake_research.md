# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/gpfs.cmake

Purpose: GPFS/VFS/pNFS-oriented preset with DBus enabled and unrelated FSALs disabled.

Important APIs/types/functions: Sets `CMAKE_PREFIX_PATH "/usr/"`, enables `USE_FSAL_GPFS`, `USE_FSAL_VFS`, `USE_FSAL_PROXY_V4`, and `USE_DBUS`, disables `USE_FSAL_CEPH`, `_MSPAC_SUPPORT`, and `USE_9P`.

Control flow: Included at configure time to bias dependency lookup and feature selection toward GPFS and VFS targets.

State and persistence behavior: CMake variables/cache behavior only.

Dependencies and integration points: Integrates with GPFS, VFS, proxy v4, pNFS, and DBus build logic; disables Ceph/MSPAC/9P to avoid incompatible or unneeded dependencies.

Risks: Hard-coding `CMAKE_PREFIX_PATH` can override user/toolchain expectations. GPFS headers/libraries may be proprietary or platform-specific and require strict environment setup.

Test signals: Configure/build in a GPFS SDK environment and verify GPFS, VFS, proxy v4, and DBus targets while Ceph/9P are absent.
