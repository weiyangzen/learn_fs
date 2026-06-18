# sources/user-network-fs/nfs-ganesha/src/log/CMakeLists.txt

## Purpose
This CMake file defines the logging object library build for Ganesha's display and log functions.

## Important APIs, Types, And Control Flow
It adds `-D__USE_GNU`, conditionally includes DBus and LTTng include directories, sets `log_STAT_SRCS` to `display.c` and `log_functions.c`, creates `add_library(log OBJECT ...)`, applies sanitizers, sets `-fPIC`, and when LTTng is enabled adds a dependency on generated trace headers and includes generated file properties. It also lists `test_display.c` as test source metadata.

## State And Persistence
Build state is persisted in generated build files and object outputs. No runtime state is defined here.

## Dependencies And Integration Points
It integrates the log object library with top-level CMake, sanitizer configuration, DBus headers for logging/stat output, and LTTng trace generation.

## Risks And Test Signals
Risks include missing generated trace header dependencies, global `add_definitions` leakage, and object library PIC requirements for shared-library consumers. Test signals include CMake configure/build with DBus on/off, LTTng on/off, sanitizer builds, and compilation of `test_display.c`.
