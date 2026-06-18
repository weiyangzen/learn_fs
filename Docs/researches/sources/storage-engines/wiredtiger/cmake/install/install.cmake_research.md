# sources/storage-engines/wiredtiger/cmake/install/install.cmake

## Purpose
`install.cmake` defines install rules for WiredTiger public headers, library targets, and POSIX pkg-config metadata.

## Important APIs, Types, And Functions
It uses `install(FILES ...)`, builds the `wt_targets` list from `ENABLE_SHARED` and `ENABLE_STATIC`, installs targets to library/archive destinations, computes `PRIVATE_PKG_LIBS`, runs `configure_file` for `wiredtiger.pc.in`, and installs the generated `.pc` file.

## Control Flow
The file always installs generated `wiredtiger.h` and source `wiredtiger_ext.h`. It conditionally appends `wiredtiger_shared` and/or `wiredtiger_static` to install targets. On POSIX builds it composes private library flags for pthread/dl/rt and enabled built-in dependencies, then configures and installs `wiredtiger.pc`.

## State And Persistence Behavior
Install state is expressed in CMake's install graph. `wiredtiger.pc` is generated in the binary directory from current version, install paths, and private dependency flags.

## Dependencies And Integration Points
It depends on `GNUInstallDirs`-style variables, library targets created elsewhere, config flags from `base.cmake`, and `wiredtiger.pc.in`. It integrates with downstream consumers through headers, libraries, and pkg-config.

## Risks
If no library flavor is enabled, `install(TARGETS ${wt_targets})` may be empty or invalid depending on CMake behavior. Private library flags must stay synchronized with `define_libwiredtiger.cmake`; drift can break static/pkg-config consumers.

## Test Signals
Run install for shared-only, static-only, POSIX, Linux, and extension-enabled builds; inspect installed headers, libraries, and `wiredtiger.pc` `Libs.private`.
