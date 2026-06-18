# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindWBclient.cmake

## Purpose

`FindWBclient.cmake` discovers a Samba Winbind4-compatible `wbclient` installation for identity and SID lookup integration.

## Important APIs, Types, and Functions

The module exports `WBCLIENT_INCLUDE_DIR`, `WBCLIENT_LIBRARIES`, `WBCLIENT_LIB_OK`, `WBCLIENT_H`, `WBCLIENT4_H`, and `WBCLIENT_FOUND`. It uses optional pkg-config, `find_path`, `find_library`, `check_library_exists`, `check_include_files`, and `check_c_source_compiles`.

## Control Flow

When `SAMBA4_PREFIX` is provided, it seeds include and library paths. On non-Windows systems it queries pkg-config module `wbclient`. It finds `wbclient.h` and library `wbclient`, checks for symbol `wbcLookupSids`, validates header inclusion with `stdint.h` and `stdbool.h`, and compiles a probe that references `enum wbcAuthUserLevel` and `WBC_AUTH_USER_LEVEL_PAC` to distinguish Winbind4 headers.

## State and Persistence Behavior

State is CMake configure/cache variables only. `CMAKE_REQUIRED_INCLUDES` is appended when checking headers.

## Dependencies and Integration Points

It depends on Samba/winbind client development files. Results feed code that integrates with Winbind for SID/account lookup and authentication metadata.

## Risks and Edge Cases

The status message prints `${WBCLIENT_LIB}`, but the discovered variable is `WBCLIENT_LIBRARIES`, so diagnostics may be blank. Required variable casing uses `WBclient_FIND_REQUIRED`, which can miss canonical package casing. `CMAKE_REQUIRED_INCLUDES` is appended globally and not restored, potentially influencing later checks.

## Test Signals

Configure against Samba4 headers/libraries, older incompatible wbclient headers, and missing packages. Compile/link of code using `wbcLookupSids` and `WBC_AUTH_USER_LEVEL_PAC` verifies the detected ABI.
