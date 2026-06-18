<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/CMakeLists.txt

Purpose: Backend-specific CMake file for the CephFS FSAL module. It defines the `fsalceph` shared module, its source list, include paths, libraries, sanitizer integration, version metadata, and install location.

Important APIs, types, and functions: Sets `_FILE_OFFSET_BITS=64`, builds `fsalceph_LIB_SRCS` from `main.c`, `export.c`, `handle.c`, `mds.c`, `ds.c`, `internal.c`, `internal.h`, and `statx_compat.h`, conditionally adds `statx_compat.c` when `CEPH_FS_CEPH_STATX` is false, includes `${CEPHFS_INCLUDE_DIR}`, creates `add_library(fsalceph MODULE ...)`, applies `add_sanitizers(fsalceph)`, links `ganesha_nfsd`, `${CEPHFS_LIBRARIES}`, `${SYSTEM_LIBRARIES}`, `${LTTNG_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`, sets version `4.2.0` and soversion `4`, and installs into `${FSAL_DESTINATION}`.

Control flow: This file is reached only when `USE_FSAL_CEPH` remains enabled in the parent build. It always includes `ds.c` in the source list, but that file's pNFS implementation is itself wrapped in `#ifdef CEPH_PNFS`. The statx compatibility source is added only when the detected CephFS headers/libraries do not provide the required statx interface.

State and persistence behavior: No runtime state is created by CMake. Build outputs are the `fsalceph` module artifact and install metadata. The compile definitions and configured `config.h` determine which Ceph feature paths are present in the final module.

Dependencies and integration points: Requires CephFS headers and libraries found by the root `find_package(CEPHFS)`. Links against the core `ganesha_nfsd` library and global system/LTTng dependencies. The module registers operations from `main.c`, including pNFS DS operations from `ds.c` when `CEPH_PNFS` is available.

Risks: `include_directories` is directory-scoped rather than target-scoped, which can leak includes to later targets in the same directory scope. `ds.c` can be present in the build but compile to an empty translation unit when `CEPH_PNFS` is not defined, so target presence alone does not prove pNFS support. Feature detection naming must remain aligned with Ceph API versions, especially for statx compatibility and pNFS-related symbols.

Test signals: A Ceph-enabled configure should print `CEPHFS_INCLUDE_DIR`, build `fsalceph`, and link without undefined symbols. Test both `CEPH_FS_CEPH_STATX` true and false environments if supported. Runtime smoke signals include module load/registration and Ceph export creation; pNFS-specific validation requires a build where `CEPH_PNFS` compiles in `pnfs_ds_ops_init`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/CMakeLists.txt -->
