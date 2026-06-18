# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/CMakeLists.txt

Purpose: this CMake file builds the plain VFS, Lustre, and dummy-Lustre FSAL shared modules from common VFS sources.

Important behavior: it defines `fsalvfs_LIB_SRCS_common` with base export, handle, syscall, file, xattr, state, sub-FSAL helper, `subfsal_vfs.c`, and `attrs.c`. Optional POSIX ACL support adds `../../posix_acls.c` and `gos` objects. `USE_FSAL_VFS` configures `main-c.in.cmake` with name `VFS`, adds `empty_check_hsm.c`, builds `fsalvfs`, links `ganesha_nfsd` and system libraries, sets version `4.2.0`, and installs it. `USE_FSAL_LUSTRE` configures a Lustre or dummy-Lustre entry point, adds `llapi_check_hsm.c`, and links `lustreapi` only when `USE_LLAPI` is true.

Control flow and state: build-time flags select module name, HSM implementation, ACL support, and link libraries. Generated `main.c`/`lustre_main.c`/`dummy_lustre_main.c` specialize the same module template.

Dependencies and integration points: consumes the `fsal_os` object library from `os/CMakeLists.txt`, Ganesha core library, optional `lustreapi`, and optional POSIX ACL support objects.

Risks: common sources are shared across modules, so changes can affect VFS and Lustre. Dummy-Lustre builds include `llapi_check_hsm.c` but without `USE_LLAPI`, relying on preprocessor no-op paths. Link options use `LDFLAG_DISALLOW_UNDEF`, so missing optional libraries surface at build time.

Test signals: configure/build plain VFS, Lustre with LLAPI, dummy Lustre without LLAPI, POSIX ACL enabled/disabled, and sanitizer/LTTng combinations.
