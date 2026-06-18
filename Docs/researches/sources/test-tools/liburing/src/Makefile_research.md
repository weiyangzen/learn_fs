# sources/test-tools/liburing/src/Makefile

## sources/test-tools/liburing/src/Makefile

Purpose: Builds and installs liburing static/shared libraries plus FFI variants.

Important targets/variables: `liburing_srcs`, `liburing_objs`, `liburing_sobjs`, `liburing_ffi_objs`; targets `liburing.a`, `liburing-ffi.a`, shared `$(libname)`, `$(ffi_libname)`, `install`, `uninstall`, `clean`; config flags for `CONFIG_NOLIBC`, `CONFIG_USE_SANITIZER`, `CONFIG_USE_TSAN`.

Control flow: include common/config files, set CPPFLAGS/CFLAGS, build normal and PIC objects, archive static libraries, link shared libraries with version scripts and sonames, install public headers/static/shared libs/symlinks, and remove them on uninstall. Config toggles add `nolibc.c`, sanitizer support, or TSAN flags.

State and persistence: creates objects, dependency files, archives, shared libraries, generated installed files and symlinks. Clean removes local artifacts and generated compat/version headers.

Dependencies/integration: relies on `configure` outputs, `Makefile.common`, `Makefile.quiet`, version maps, liburing source files, compiler/linker/archive tools.

Risks: nolibc uses freestanding/no-default-libs flags and libgcc path, so architecture config must be correct. Shared link uses `-z defs` unless sanitizer, catching unresolved symbols. Install path symlink logic depends on `relativelibdir`.

Test signals: CI multi-arch build/install and test_build linkage; static/shared artifacts existence.
