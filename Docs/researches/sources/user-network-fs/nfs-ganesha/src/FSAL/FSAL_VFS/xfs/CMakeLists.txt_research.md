# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/CMakeLists.txt

## Purpose

This CMake file builds the XFS FSAL module as a loadable module using the common FSAL_VFS sources plus XFS-specific syscall and sub-FSAL glue. The source was read as a complete 56-line file.

## Important APIs, Types, and Functions

Build targets are `fsalxfs` and optional imported `handle`. `fsalxfs_LIB_SRCS` includes `main.c`, shared VFS `export.c`, `handle.c`, `file.c`, `xattrs.c`, `state.c`, `empty_check_hsm.c`, `vfs_methods.h`, and XFS `handle_syscalls.c`/`subfsal_xfs.c`. It adds `-D__USE_GNU`, sanitizer integration, version `4.2.0`, SOVERSION `4`, and installation to `${FSAL_DESTINATION}`.

## Control Flow

At configure/generate time CMake defines the source list, creates a module library, optionally imports libhandle from `PATH_LIBHANDLE`, links `ganesha_nfsd`, system libraries, undefined-symbol protection, and `handle`, then emits install rules.

## State and Persistence Behavior

No runtime state is owned by this file. It controls build artifacts and install layout for the XFS FSAL shared object.

## Dependencies and Integration Points

The important external dependency is XFS libhandle, exposed as `handle` and used by `handle_syscalls.c`. The module integrates common FSAL_VFS implementation with XFS-specific handle support.

## Risks and Edge Cases

`target_link_libraries(fsalxfs handle)` is unconditional even though the imported target is only created under `PATH_LIBHANDLE`; builds rely on a system `handle` library or CMake target resolution. Source-list drift can silently omit common VFS behavior from the module.

## Test Signals

Build with and without explicit `PATH_LIBHANDLE`, run link-time undefined-symbol checks, verify installed module naming/version, and run FSAL_XFS smoke tests that require libhandle symbols.
