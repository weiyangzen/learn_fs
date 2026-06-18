# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindUnwind.cmake

## Purpose

`FindUnwind.cmake` discovers libunwind headers and library for stack unwinding support.

## Important APIs, Types, and Functions

The module accepts `UNWIND_PATH_HINT` and exports `UNWIND_FOUND`, `UNWIND_INCLUDE_DIR`, `UNWIND_LIBRARY`, and `UNWIND_LIBRARIES`. It uses `find_path`, `find_library`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

## Control Flow

The module reports a path hint when provided, searches for `libunwind.h` in include suffixes, searches for library `unwind` in `lib` and `lib64`, sets `UNWIND_LIBRARIES`, validates required include/library variables, and marks them advanced.

## State and Persistence Behavior

Only CMake cache/configure variables are changed.

## Dependencies and Integration Points

It depends on libunwind development files. Consumers can link `${UNWIND_LIBRARIES}` for crash diagnostics, stack traces, or backtrace-enabled logging.

## Risks and Edge Cases

Some platforms split libunwind into architecture-specific or local/unwind-generic libraries; this module only searches `unwind`. It does not check symbols or ABI flavor.

## Test Signals

Configure with and without `UNWIND_PATH_HINT`, then compile/link a small target that includes `libunwind.h` and calls an unwind API. Runtime stack capture is the final integration signal.
