# sources/user-network-fs/libsmb2/cmake/FindSMB2.cmake

Purpose: This is a CMake find-module for consumers that want to locate an installed libsmb2 library.

Important APIs and types: It optionally uses `pkg_check_modules(PC_SMB2 libsmb2 QUIET)` when `PKG_CONFIG_FOUND` is already true, then uses `find_path`, `find_library`, and `find_package_handle_standard_args`. Output variables are `SMB2_FOUND`, `SMB2_INCLUDE_DIRS`, `SMB2_LIBRARIES`, `SMB2_DEFINITIONS`, and `SMB2_VERSION`.

Control flow: The module looks for `smb2/libsmb2.h`, records the pkg-config version, finds library `smb2`, invokes standard package handling, and, when found, maps the singular include/library values into plural consumer variables and sets `-DHAVE_LIBSMB2=1`.

State and persistence behavior: It only mutates CMake cache variables such as `SMB2_INCLUDE_DIR` and `SMB2_LIBRARY`; there is no filesystem output.

Dependencies and integration points: It is installed by the root CMake script and consumed by downstream projects with `find_package(SMB2)`.

Risks: The module references pkg-config variables only if `PKG_CONFIG_FOUND` was set by the caller; it does not call `find_package(PkgConfig)` itself. It provides variables rather than an imported target, so downstream consumers must manually apply include dirs, libraries, and definitions.

Test signals: Install libsmb2, configure a small downstream project with `find_package(SMB2 REQUIRED)`, and verify the include directory, library path, version, and compile definition are populated.
