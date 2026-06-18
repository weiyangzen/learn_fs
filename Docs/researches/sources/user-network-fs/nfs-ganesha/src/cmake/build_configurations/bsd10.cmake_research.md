# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/bsd10.cmake

Purpose: FreeBSD 10.1-oriented build preset that narrows the build to VFS-like support by disabling several optional FSALs and services.

Important APIs/types/functions: Sets `USE_FSAL_PROXY_V4`, `USE_FSAL_CEPH`, `USE_FSAL_GPFS`, `_MSPAC_SUPPORT`, `USE_9P`, and `USE_DBUS` to `OFF`, then emits a status message.

Control flow: Included by the top-level build when the BSD 10.1 configuration is selected; variables influence later `goption`, `find_package`, and subdirectory decisions.

State and persistence behavior: CMake cache/configuration state only.

Dependencies and integration points: Integrates with top-level option handling and platform-specific dependency discovery, especially avoiding unsupported Linux-centric dependencies on FreeBSD.

Risks: The comment says only VFS FSAL, but the file relies on defaults for any options not explicitly disabled. Future FSAL options may need explicit handling to preserve the minimal preset.

Test signals: Configure on FreeBSD-like and Linux hosts with this preset and verify disabled FSALs are not discovered or built.
