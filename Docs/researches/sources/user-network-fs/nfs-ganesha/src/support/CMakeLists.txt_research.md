<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/support/CMakeLists.txt

## Purpose
This CMake file defines the object libraries that make up NFS-Ganesha's support-layer code: string utilities, hash functions, UID/group mapping, netgroup cache, and the main support object library.

## Important APIs, Types, and Functions
The build targets are `string_utils`, `hash`, `uid2grp`, `netgroup_cache`, and `support`, all created as `OBJECT` libraries with `-fPIC` and passed through `add_sanitizers`. Source groups include `strlcpy.c`, `strnlen.c`, `refstr.c`, `murmur3.c`, `city.c`, `uid2grp.c`, `uid2grp_cache.c`, `netgroup_cache.c`, and the larger `support_STAT_SRCS` list containing ACL, credential, filehandle, config, conversion, data-server, export, delayed execution, base64, stats, transport, and IP utilities. `err_inject.c` is included only under `ERROR_INJECTION`.

## Control Flow
CMake conditionally adds DBus include directories when `USE_DBUS` is enabled. For each object library it attaches sanitizer settings and PIC flags. Under `USE_LTTNG`, selected targets depend on generated trace headers and include generated file properties.

## State and Persistence Behavior
The file produces build-system state: object library targets, compile flags, dependencies, and source lists. It does not install files directly in the shown content.

## Dependencies and Integration Points
It depends on top-level CMake variables such as `USE_DBUS`, `DBUS_INCLUDE_DIRS`, `USE_LTTNG`, and `ERROR_INJECTION`, plus project macros like `add_sanitizers`. These object libraries are consumed by higher-level daemon and test targets.

## Risks and Test Signals
Risks include missing trace-header dependencies for sources that include generated LTTng headers, inconsistent PIC/sanitizer settings across object libraries, and optional `err_inject.c` compiling unused globals. Test signals are clean CMake configure for DBus/LTTng/error-injection permutations and successful link of binaries consuming the support object libraries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/CMakeLists.txt -->
