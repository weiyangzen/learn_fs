# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLibACL.cmake

## Purpose

`FindLibACL.cmake` probes POSIX ACL header and library capabilities used by Ganesha ACL handling. It distinguishes Linux-style `acl/libacl.h` with `libacl` from systems such as FreeBSD that expose ACL APIs directly through `sys/acl.h`.

## Important APIs, Types, and Functions

The module uses `check_include_files`, `find_library`, `check_library_exists`, and `check_symbol_exists`. It sets feature variables such as `HAVE_SYS_ACL_H`, `HAVE_ACL_LIBACL_H`, `LIBACL_LIBRARY`, `HAVE_LIBACL`, `HAVE_ACL_GET_FD_NP`, and `HAVE_ACL_SET_FD_NP`.

## Control Flow

The configure step checks for `sys/acl.h` and `acl/libacl.h`, searches for library `acl`, validates `acl_get_file` when the libacl header is available, and checks FreeBSD-style `acl_get_fd_np` and `acl_set_fd_np` symbols when `sys/acl.h` exists.

## State and Persistence Behavior

All outputs are CMake feature/cache variables consumed by generated `config.h` or conditional build logic. The module does not create files or targets.

## Dependencies and Integration Points

It depends on CMake check modules being included by the parent build and on platform ACL headers/libraries. Results affect FSAL and permission code that needs ACL calls.

## Risks and Edge Cases

There is no `FindPackageHandleStandardArgs` call or canonical `LIBACL_FOUND`, so callers must rely on individual feature variables. Header/library mismatches can produce partial capability flags. `check_library_exists` is guarded by `HAVE_ACL_LIBACL_H`, which is reasonable on Linux but may miss nonstandard packaging.

## Test Signals

Configure on Linux with `libacl-devel`, Linux without it, and FreeBSD-like environments should exercise the expected combinations. Compile tests for files using `acl_get_file`, `acl_get_fd_np`, and `acl_set_fd_np` confirm the feature variables are wired correctly.
