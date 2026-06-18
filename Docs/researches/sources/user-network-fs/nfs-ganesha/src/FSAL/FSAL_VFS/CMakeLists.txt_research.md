# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/CMakeLists.txt

Purpose: this top-level CMake file configures the VFS-family FSAL build directory.

Important behavior: it adds `-D__USE_GNU`, includes the current source directory so generated sub-FSAL entry points can include local headers, sets `LIB_PREFIX`, always adds the `os` object-library subdirectory, and conditionally adds `vfs` for `USE_FSAL_VFS` or `USE_FSAL_LUSTRE`, and `xfs` for `USE_FSAL_XFS`.

Control flow and state: CMake options select platform object code first, then module-specific shared objects. There is no runtime state in this file.

Dependencies and integration points: feeds `FSAL_VFS/os` and `FSAL_VFS/vfs` build scripts. The generated Lustre/VFS module entry point in the build tree depends on current-directory include paths.

Risks: `__USE_GNU` changes libc feature visibility and is required for GNU extensions used by VFS file operations. Conditional subdirectory logic must match top-level option definitions; otherwise VFS shared modules may not be built.

Test signals: configure with `USE_FSAL_VFS`, `USE_FSAL_LUSTRE`, `USE_LLAPI`, `USE_FSAL_XFS`, Linux, and FreeBSD combinations and verify the expected module targets are present.
