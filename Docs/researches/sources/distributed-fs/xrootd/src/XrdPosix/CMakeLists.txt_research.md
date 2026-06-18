# sources/distributed-fs/xrootd/src/XrdPosix/CMakeLists.txt

## Purpose
Defines the CMake build targets for XRootD POSIX client libraries: the main `XrdPosix` shared library and the `XrdPosixPreload` shared library used for preload/interposition.

## Important APIs, Types, and Functions
- `add_library(XrdPosix SHARED ...)` compiles POSIX admin, cache, callback, config, dir, file, object, prep IO, stats, trace, and xrootd path/source files.
- `target_link_libraries(XrdPosix PRIVATE XrdCl XrdUtils ${CMAKE_THREAD_LIBS_INIT})`.
- `set_target_properties(XrdPosix PROPERTIES SOVERSION ... VERSION ...)`.
- `add_library(XrdPosixPreload SHARED ...)` builds preload/linkage sources.
- `target_link_libraries(XrdPosixPreload PRIVATE XrdPosix ${CMAKE_DL_LIBS})`.
- `install(TARGETS XrdPosix XrdPosixPreload LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})`.

## Control Flow
Build flow first defines the main POSIX shared library and links it against client/utils/thread libraries. It then defines the preload shared library that links to `XrdPosix` and dynamic loader libraries. Both targets receive version metadata and are installed as libraries.

## State and Persistence Behavior
CMake target state affects generated build system outputs and installed shared libraries. No runtime persistence is defined here.

## Dependencies and Integration Points
Integrates with top-level XRootD CMake variables `XRootD_VERSION_MAJOR`, `XRootD_LIBVERSION`, `CMAKE_THREAD_LIBS_INIT`, `CMAKE_DL_LIBS`, and `CMAKE_INSTALL_LIBDIR`. Source list integration determines which POSIX components participate in the library ABI.

## Risks and Test Signals
Risks include missing source/header entries after file renames, incorrect private link dependencies for downstream symbol resolution, and platform-specific preload/dl behavior. Build tests should compile both targets, inspect linked libraries, verify versioned sonames, and run install packaging checks.
