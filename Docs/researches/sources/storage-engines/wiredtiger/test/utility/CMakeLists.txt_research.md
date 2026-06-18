# sources/storage-engines/wiredtiger/test/utility/CMakeLists.txt

## Purpose

This CMake file builds the shared `test_util` static library used by WiredTiger C tests.

## Important APIs, Types, and Functions

It defines the `sources` list (`backup.c`, `disagg.c`, `file.c`, `lazyfs.c`, `misc.c`, `parse_opts.c`, `thread.c`, `tiered.c`, `util_modify.c`, `util_random.c`), creates `add_library(test_util STATIC ...)`, enables position-independent code, adds public include directories, links `wt::wiredtiger`, and conditionally includes/links Windows shims.

## Control Flow

At configure/build time, CMake assembles the static library and applies diagnostic compile flags. Consumers link test helper APIs through this target.

## State and Persistence Behavior

Build artifacts include `libtest_util` and propagated include paths. No runtime state is created by the CMake file itself.

## Dependencies and Integration Points

Integrates with the WiredTiger target, generated include/config directories, source include tree, Windows test support, and compiler diagnostic settings.

## Risks and Edge Cases

Adding helper source files requires updating this list. Include-directory order affects whether generated headers are found before source headers.

## Test Signals

Signals are successful compilation/linking of `test_util` and downstream tests resolving helper symbols.
