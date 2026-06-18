<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/os/CMakeLists.txt

## Purpose
This CMake file selects platform-specific OS abstraction sources and builds them into the `gos` object library.

## Important APIs, Types, and Functions
It sets `gos_STAT_SRCS` based on platform flags. FreeBSD uses `freebsd/atsyscalls.c`, `freebsd/mntent_compat.c`, `freebsd/subr.c`, and `freebsd/xattr.c`. Darwin uses `darwin/sys_resource.c`. Linux uses `linux/acl.c` and `linux/subr.c`. It then calls `add_library(gos OBJECT ...)`, applies sanitizers, sets `-fPIC`, and adds LTTng generated-header dependencies when `USE_LTTNG` is enabled.

## Control Flow
Only one platform block should populate `gos_STAT_SRCS` in a normal build. After source selection, target setup is unconditional. LTTng-specific generated file properties are included only under `USE_LTTNG`.

## State and Persistence Behavior
The file persists build graph state: selected source list, object target, compile flags, sanitizer instrumentation, and optional generated header dependency. It has no runtime state.

## Dependencies and Integration Points
It depends on top-level CMake variables `FREEBSD`, `DARWIN`, `LINUX`, `USE_LTTNG`, `CMAKE_BINARY_DIR`, `add_sanitizers`, and the generated file `gsh_lttng_generation_file_properties.cmake`. The `gos` object library provides OS abstraction functions used by FSAL and support code.

## Risks and Edge Cases
If no platform variable is set, `gos_STAT_SRCS` will be empty or undefined and target creation can fail or produce an empty object library. If multiple platform variables are true, later `SET()` calls overwrite earlier selections. Platform-specific source coverage must stay synchronized with headers under `include/os`.

## Test Signals
Configure/build tests on Linux, FreeBSD, and Darwin should confirm the intended source list and successful `gos` object creation. LTTng-enabled builds should verify generated-header ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/os/CMakeLists.txt -->
