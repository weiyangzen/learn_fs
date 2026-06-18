# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindReadline.cmake

## Purpose

`FindReadline.cmake` locates GNU Readline headers and library for any interactive command or utility support built by NFS-Ganesha.

## Important APIs, Types, and Functions

It defines `READLINE_INCLUDE_DIR`, `READLINE_LIBRARY`, and `READLINE_FOUND` via `FIND_PATH` and `FIND_LIBRARY`, then emits status or fatal diagnostics based on `Readline_FIND_QUIETLY` and `Readline_FIND_REQUIRED`.

## Control Flow

The module searches for `readline/readline.h` and `libreadline`. If both are found, it marks the package found and reports the library unless quiet. If not found and required, it aborts configuration.

## State and Persistence Behavior

Only CMake variables are changed. There is no file generation or target mutation.

## Dependencies and Integration Points

It depends on GNU Readline development files. Consumers must add include directories and link libraries themselves based on the exported variables.

## Risks and Edge Cases

There is no symbol/version check and no `FindPackageHandleStandardArgs`. It does not include terminal dependency libraries such as `ncurses`, so final link may still fail on systems where readline does not carry transitive metadata.

## Test Signals

Configure with Readline installed/missing and link any utility that uses Readline. A stricter smoke test should compile a small include of `readline/readline.h` and link a `readline()` call.
