# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCEPHFS.cmake

Purpose: Finds CephFS headers/libraries and detects optional libcephfs API capabilities that control FSAL_CEPH feature macros.

Important APIs/types/functions: Consumes optional `CEPH_PREFIX`; sets `CEPHFS_INCLUDE_DIR`, `CEPHFS_LIBRARY_DIR`, `CEPHFS_LIBRARY`, `CEPHFS_LIBRARIES`, and feature variables such as `USE_FSAL_CEPH_MKNOD`, `USE_FSAL_CEPH_SETLK`, `USE_FSAL_CEPH_LL_LOOKUP_ROOT`, `USE_FSAL_CEPH_LL_DELEGATION`, `USE_FSAL_CEPH_LL_SYNC_INODE`, `USE_CEPH_LL_FALLOCATE`/related fallocate variables, `USE_FSAL_CEPH_ABORT_CONN`, `USE_FSAL_CEPH_RECLAIM_RESET`, `USE_FSAL_CEPH_GET_FS_CID`, `USE_FSAL_CEPH_REGISTER_CALLBACKS`, `USE_FSAL_CEPH_LOOKUP_VINO`, `USE_FSAL_CEPH_STATX`, and nonblocking/zerocopy toggles.

Control flow: Prefix hints are searched first with `NO_DEFAULT_PATH`; fallback searches use default paths. The module verifies `ceph_ll_lookup` to accept the library, clears include/library cache on failure, then runs many `check_library_exists()` and `check_symbol_exists()` probes to enable or disable feature-specific compile definitions. It finishes with `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

State and persistence behavior: CMake cache and feature variables only. It may unset cached include/library dirs when a required symbol is missing.

Dependencies and integration points: Requires CMake library/symbol check modules, libcephfs, `cephfs/libcephfs.h`, and FSAL_CEPH source conditionals that consume the feature variables.

Risks: There is a variable inconsistency around fallocate (`USE_CEPH_FALLOCATE` vs `USE_CEPH_LL_FALLOCATE`). `CEPHFS_LIBRARIES` is set even when the library is missing. Some messages mention different symbol names than checked. API probes are numerous and need maintenance as Ceph evolves.

Test signals: Configure against old and new Ceph versions, with `CEPH_PREFIX`, without Ceph, and verify generated config headers/compile definitions match available symbols.
