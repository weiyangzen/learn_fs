# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLTTng.cmake

## Purpose

`FindLTTng.cmake` discovers the LTTng userspace tracing development files and command-line tool for optional tracepoint support in NFS-Ganesha. It supports an explicit `LTTNG_PATH_HINT`, locates UST and control headers/libraries, and exports variables used by higher-level build logic when enabling LTTng instrumentation.

## Important APIs, Types, and Functions

The module defines CMake cache/results variables `LTTNG_FOUND`, `LTTNG_EXECUTABLE`, `LTTNG_LIBRARIES`, `LTTNG_INCLUDE_DIR`, `LTTNG_CTL_LIBRARIES`, and `LTTNG_CTL_INCLUDE_DIR`. Discovery is performed with `find_path`, `find_library`, `find_program`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

If `LTTNG_PATH_HINT` is set, the module reports that hint and uses it in all path searches. It first finds `lttng/tracepoint.h`, the `liblttng-ust.so` directory, `lttng-ust`, and `uuid`. It then optionally finds `lttng-ust-common`, adding it to `LTTNG_LIBRARIES` when present. A second pass finds `lttng/lttng.h` and `lttng-ctl`, then searches for an `lttng` or `lttng-ctl` executable.

## State and Persistence Behavior

State is limited to CMake cache variables and advanced cache entries for include/library directories. There is no filesystem mutation beyond CMake cache/configure behavior.

## Dependencies and Integration Points

The module depends on LTTng UST, LTTng control headers/libraries, `libuuid`, and CMake's `FindPackageHandleStandardArgs`. It integrates with targets that compile generated tracepoint code or link Ganesha against LTTng support.

## Risks and Edge Cases

`LTTNG_LIBRARIES` includes `UUID_LIBRARY` but package handling does not require `LTTNG_EXECUTABLE` or `LTTNG_CTL_LIBRARY`, despite separately discovering them. The second `find_program` mistakenly writes to `LEX_PROGRAM`, so default-path executable discovery may not update `LTTNG_EXECUTABLE`. Reusing `LTTNG_LIBRARY_DIR` for both UST and UST common can also hide partial installs.

## Test Signals

Useful signals are configure runs with and without `LTTNG_PATH_HINT`, builds with `USE_LTTNG`, generated trace header dependencies, and link checks confirming `lttng-ust`, optional `lttng-ust-common`, `lttng-ctl`, and `uuid` are all resolvable.
