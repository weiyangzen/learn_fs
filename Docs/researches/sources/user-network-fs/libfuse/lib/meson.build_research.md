# sources/user-network-fs/libfuse/lib/meson.build

Purpose: `lib/meson.build` defines how the `fuse3` shared library is assembled, which platform-specific source files and optional features are included, what dependencies are linked, and how pkg-config metadata is generated.

Important APIs, types, and functions: It declares `libfuse_sources`, conditionally appends mount backends, service implementation or stub, iconv module, io_uring implementation, and optional libraries. It builds `library('fuse3', ...)` with version script linkage, `FUSE_USE_VERSION=319`, and `FUSERMOUNT_DIR`. It emits a `fuse3` pkg-config file and a Meson dependency object `libfuse_dep`.

Control flow: Meson conditionals select Linux vs BSD mount code, new mount API source, service-mount source vs stub, iconv support and optional `libiconv`, io_uring support with `liburing` and `numa`, dynamic loading, NetBSD perfuse/puffs, or `rt`. If service-mount is enabled it also adds pkg-config variables for service socket directory and permissions.

State and persistence behavior: This is build-time state only. It controls which compiled objects and dependency metadata persist in build outputs and installed pkg-config files.

Dependencies and integration points: It integrates configuration probes from `private_cfg`, project version variables, `include_dirs`, `base_version`, `service_socket_perms`, the linker version script, and platform dependency discovery. Its source selection directly determines whether `fuse_service.c`, `fuse_service_stub.c`, `modules/iconv.c`, and `fuse_uring.c` are part of the library.

Risks: Missing conditional dependencies will produce link failures only in specific feature matrices. `libraries_private` is hardcoded to `-ldl` even though `libdl` is optional, which may be wrong on platforms without libdl. Optional iconv handling must work both when iconv is in libc and when a separate library exists. Version-script link args are GNU-ld-specific and may need platform gating.

Test signals: CI should build Linux, BSD/NetBSD, service/no-service, iconv/no-iconv, uring/no-uring, new-mount-api/no-new-mount-api, and non-GNU linker configurations. Installed pkg-config output should include correct public/private libs and service variables only when enabled.
