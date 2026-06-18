# sources/storage-engines/wiredtiger/cmake/define_libwiredtiger.cmake

## Purpose
`define_libwiredtiger.cmake` centralizes creation of `libwiredtiger` CMake library targets so static and shared variants receive consistent properties, include directories, compile flags, and dependencies.

## Important APIs, Types, And Functions
The macro `define_wiredtiger_library(target type SOURCES ... PUBLIC_INCLUDES ... PRIVATE_INCLUDES ...)` validates arguments, calls `add_library`, attaches includes, applies diagnostic C flags, sets output name/properties, and links system and optional third-party libraries.

## Control Flow
After argument parsing and source validation, the macro defines the target, attaches include paths, applies `COMPILER_DIAGNOSTIC_C_FLAGS`, sets `OUTPUT_NAME` to `wiredtiger`, `NO_SYSTEM_FROM_IMPORTED`, and `C_STANDARD 11`, then links `Threads::Threads`, `${CMAKE_DL_LIBS}`, Linux `rt`, memkind, built-in compressors/encryption, IAA support, accel-config, and key provider as enabled.

## State And Persistence Behavior
The macro creates build-system target state. The output library name is deliberately the same for each flavor, so call sites must avoid conflicting variants in the same output context.

## Dependencies And Integration Points
It integrates with options from `base.cmake`, third-party targets from `cmake/third_party`, and installation in `install.cmake`. It is the main target-definition hook for WiredTiger library builds.

## Risks
Because this is a macro, variables are evaluated in caller scope and naming conflicts are possible. Optional dependency flags must stay aligned with discovery modules and pkg-config private library generation. Multiple targets with the same output name can collide if build directories are not configured correctly.

## Test Signals
Configure shared-only, static-only, built-in extension, memkind, IAA, Linux, and non-Linux builds; verify target link lines and final library names.
