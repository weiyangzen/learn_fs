# sources/user-network-fs/libsmb2/cmake/Modules/FindGSSAPI.cmake

Purpose: This module locates GSSAPI for platforms where libsmb2 can use GSSAPI authentication support, notably the iOS branch in the root CMake file.

Important APIs and types: It uses `find_library(GSSAPI_LIBRARY NAMES gssapi_krb5)`, `find_path(GSSAPI_INCLUDE_DIR NAMES gssapi.h gssapi/gssapi.h)`, and `find_package_handle_standard_args`.

Control flow: The module searches for the library and header, runs standard required-variable handling, and, if found, assigns `GSSAPI_LIBRARIES` and `GSSAPI_INCLUDE_DIRS`.

State and persistence behavior: It writes only CMake cache variables and normal variables. There is no generated file.

Dependencies and integration points: It is loaded from the custom CMake module path when `ENABLE_GSSAPI` is on for iOS. Its output feeds `CORE_LIBRARIES` in the root build.

Risks: The condition `if (GSSAPI_LIBRARY AND GSSAPI_INCLUDE_DIRS)` checks the plural include variable before it is assigned; the standard package handler still sets `GSSAPI_FOUND`, but the extra condition is ineffective or misleading. The module searches only `gssapi_krb5`, which may not match all platform GSSAPI library names.

Test signals: Configure with `ENABLE_GSSAPI=ON` on a target sysroot containing GSSAPI and verify `GSSAPI_FOUND`, include path, and library path are set and linked into the core target.
