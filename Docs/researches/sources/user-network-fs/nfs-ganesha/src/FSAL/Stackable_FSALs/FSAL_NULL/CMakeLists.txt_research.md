<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/CMakeLists.txt

## Purpose

This CMake file builds the NULL stackable FSAL as the `fsalnull` module. NULLFS is a pass-through stackable FSAL used to layer on top of another FSAL while preserving a separate module boundary and operation vector.

## Important APIs, Types, and Functions

- `add_definitions(-D__USE_GNU)`: enables GNU extensions for this module build.
- `fsalnull_LIB_SRCS`: includes `handle.c`, `file.c`, `xattrs.c`, `nullfs_methods.h`, `main.c`, and `export.c`.
- `add_library(fsalnull MODULE ...)`: builds a loadable FSAL module rather than a static/shared library consumed normally by linkers.
- `add_sanitizers(fsalnull)`: ties the module into the repository sanitizer configuration.
- `target_link_libraries(fsalnull ganesha_nfsd ${LDFLAG_DISALLOW_UNDEF})`: links against core Ganesha and rejects unresolved symbols when configured.
- Optional LTTng dependency generation is wired under `USE_LTTNG`.

## Control Flow

At configure time, the file defines compile options, source membership, optional trace-generation dependency, link libraries, module version properties, and install destination. It does not contain runtime control flow.

## State and Persistence Behavior

The only persistent artifact is the generated module library and its installation into `${FSAL_DESTINATION}` as component `fsal`. Version metadata is set to `4.2.0` with `SOVERSION 4`.

## Dependencies and Integration Points

The module expects symbols from `ganesha_nfsd`, the FSAL module loader, and the generated LTTng trace headers when tracing is enabled. The source list corresponds to the NULLFS operation implementations and must remain synchronized with function declarations in `nullfs_methods.h`.

## Risks and Edge Cases

- Omitting a new NULLFS source file from `fsalnull_LIB_SRCS` will produce missing behavior or unresolved symbols.
- `${LDFLAG_DISALLOW_UNDEF}` is useful for catching missing symbols early but can expose platform/linker-specific incompatibilities.
- The hardcoded module version should be updated only in line with project release conventions.

## Test Signals

Build tests should confirm `fsalnull` compiles with and without `USE_LTTNG`, links without undefined symbols, and installs to the expected FSAL module directory. Runtime smoke tests should verify the module can be loaded by name `NULL`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/CMakeLists.txt -->
