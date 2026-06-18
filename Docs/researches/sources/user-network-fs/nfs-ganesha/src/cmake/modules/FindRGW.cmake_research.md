# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindRGW.cmake

## Purpose

`FindRGW.cmake` discovers Ceph RGW file-interface support for the RGW FSAL. It finds librgw headers/libraries, verifies core and optional symbols, and extracts the `rgw_file.h` version.

## Important APIs, Types, and Functions

The module exports `RGW_FOUND`, `RGW_INCLUDE_DIR`, `RGW_LIBRARY_DIR`, `RGW_LIBRARY`, `RGW_LIBRARIES`, `RGW_FILE_VERSION`, `USE_FSAL_RGW_MOUNT2`, and `USE_FSAL_RGW_XATTRS`. It uses `find_path`, `find_library`, `check_library_exists`, `file(STRINGS)`, regex extraction, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

With `RGW_PREFIX`, discovery searches only under that prefix first. It then falls back to default paths for `include/rados/librgw.h` and `librgw.so`. It finds `rgw`, checks for required `rgw_mount`, then probes optional `rgw_mount2` and `rgw_getxattrs` to set feature toggles. It reads version macros from `${RGW_INCLUDE_DIR}/include/rados/rgw_file.h` and validates include/library directory variables.

## State and Persistence Behavior

State is CMake cache/configuration state. It can clear include/library directory cache entries when the required symbol is missing.

## Dependencies and Integration Points

It depends on librgw from Ceph and CMake symbol checks. Results drive conditional compilation of RGW FSAL functionality and compatibility code paths for older librgw versions.

## Risks and Edge Cases

The header search name includes `include/rados/librgw.h`, so `RGW_INCLUDE_DIR` may be a prefix rather than a normal include directory. Optional feature flags are global variables that must be consumed consistently by compile definitions. Package handling does not require `RGW_LIBRARY` directly.

## Test Signals

Configure against Ceph versions with and without `rgw_mount2` and `rgw_getxattrs`. Compile/link of RGW FSAL and tests that exercise mount and xattr code paths confirm feature flags.
