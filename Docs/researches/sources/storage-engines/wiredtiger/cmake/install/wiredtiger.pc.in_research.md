# sources/storage-engines/wiredtiger/cmake/install/wiredtiger.pc.in

## Purpose
`wiredtiger.pc.in` is the pkg-config template for installed WiredTiger development metadata.

## Important APIs, Types, And Functions
It defines `prefix`, `exec_prefix`, `libdir`, `includedir`, package name/description, version, linker flags, compiler flags, and `Libs.private`.

## Control Flow
`install.cmake` substitutes CMake install directories, version numbers, and `PRIVATE_PKG_LIBS` using `configure_file(... @ONLY)`.

## State And Persistence Behavior
The generated `wiredtiger.pc` is installed under `${CMAKE_INSTALL_LIBDIR}/pkgconfig` on POSIX builds and is consumed by downstream builds.

## Dependencies And Integration Points
It integrates with pkg-config consumers and the install rules. `Libs.private` is composed from the same optional libraries that libwiredtiger links privately.

## Risks
Incorrect private libs or install directories can break static linking or cross-prefix installs. The empty `Requires:` field means dependency propagation relies on explicit linker flags.

## Test Signals
After install, run `pkg-config --cflags --libs wiredtiger` and `pkg-config --static --libs wiredtiger` for baseline and extension-enabled builds.
