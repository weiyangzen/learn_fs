# sources/user-network-fs/nfs-ganesha/src/cmake/modules/LibFindMacros.cmake

## Purpose

`LibFindMacros.cmake` provides reusable CMake helper macros/functions for writing find modules. It wraps dependency discovery, pkg-config probing, version-header extraction, and final package result processing.

## Important APIs, Types, and Functions

Public helpers are `libfind_package(PREFIX PKG ...)`, `libfind_pkg_check_modules(...)`, `libfind_pkg_detect(PREFIX ...)`, `libfind_version_header(PREFIX VERSION_H DEFINE_NAME [QUIET])`, and `libfind_process(PREFIX)`.

## Control Flow

`libfind_package` forwards `REQUIRED` from the parent package and records dependencies. `libfind_pkg_detect` parses `FIND_PATH` and `FIND_LIBRARY` sections, runs quiet pkg-config, then searches for requested headers/libraries using pkg-config hints. `libfind_version_header` reads a header and extracts a string-valued `#define`. `libfind_process` aggregates include/library option variables from the package and dependencies, removes duplicates, checks missing values, validates requested versions, marks variables advanced on success, exports plural result variables, or emits detailed fatal/warning diagnostics.

## State and Persistence Behavior

The helpers mutate CMake variables in parent scope and mark cache entries advanced or visible. They do not create files or targets.

## Dependencies and Integration Points

The module depends optionally on CMake `FindPkgConfig`. `FindRDMA.cmake` uses it for ibverbs/rdmacm component discovery, and other local find modules can reuse it.

## Risks and Edge Cases

There is a likely typo in `libfind_process`: `({i}_INCLUDE_DIR STREQUAL ...` lacks `${`, which could affect dependency option inference. The macros assume conventional singular/plural variable names and can fatal if a dependency exports unusual names. Version extraction only supports quoted string defines.

## Test Signals

Exercise with simple packages found by pkg-config, packages without pkg-config, dependency chains, missing headers, missing libraries, and version constraints. Run configure with `LIBFIND_DEBUG` to verify exported include/library lists.
