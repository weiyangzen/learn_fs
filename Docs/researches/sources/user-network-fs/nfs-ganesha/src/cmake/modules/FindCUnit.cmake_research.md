# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCUnit.cmake

Purpose: Finds CUnit library and headers for C unit test builds.

Important APIs/types/functions: Consumes `CUNIT_PREFIX`; sets `CUNIT_LIBRARIES` from library `cunit` and `CUNIT_INCLUDE_DIR` from `CUnit/Basic.h`; uses `find_package_handle_standard_args`.

Control flow: Searches library and include path, then reports success only if both are present.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Test targets using CUnit consume the discovered include/library variables.

Risks: Library name casing and platform package naming can vary. It searches `${CUNIT_PREFIX}` directly for libraries but `${CUNIT_PREFIX}/include` for headers, which may miss lib/lib64 under a prefix.

Test signals: Configure tests with system CUnit, custom prefix, and missing library/header combinations.
