# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRADOS.cmake

## Purpose

`FindRADOS.cmake` discovers Ceph librados for Ceph-backed FSALs, RADOS recovery storage, and RADOS-backed configuration URL support. It supports `RADOS_PREFIX`, locates headers/libraries, and checks for a required librados operation symbol.

## Important APIs, Types, and Functions

The module exports `RADOS_FOUND`, `RADOS_INCLUDE_DIR`, `RADOS_LIBRARY_DIR`, `RADOS_LIBRARY`, and `RADOS_LIBRARIES`. It uses `find_path`, `find_library`, `check_library_exists`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

With `RADOS_PREFIX`, it first searches only under the prefix for `rados/librados.h` and `librados.so`. Missing pieces are retried in default paths. It then finds library `rados` within `RADOS_LIBRARY_DIR` and validates symbol `rados_read_op_omap_get_vals2`. If the symbol check fails, it clears cached include/library directory variables. Package handling requires the include and library directories.

## State and Persistence Behavior

The module writes CMake cache variables and can unset stale cache entries. It does not create build targets.

## Dependencies and Integration Points

It depends on Ceph librados and CMake check modules. Results are consumed by Ceph FSAL, RADOS recovery, and `ganesha_rados_urls` module linkage.

## Risks and Edge Cases

`FIND_PACKAGE_HANDLE_STANDARD_ARGS` requires `RADOS_LIBRARY_DIR` but not `RADOS_LIBRARY`, so a directory can pass even if the actual library variable is problematic. The symbol check uses `RADOS_LIBRARY_DIR` as the location argument and assumes linker search behavior. The unconditional status message may print `RADOS_LIBRARY-NOTFOUND`.

## Test Signals

Configure against supported and too-old Ceph versions to validate the symbol gate. Build and link of `conf_url_rados.c`, FSAL_CEPH, and RADOS recovery code are key signals.
