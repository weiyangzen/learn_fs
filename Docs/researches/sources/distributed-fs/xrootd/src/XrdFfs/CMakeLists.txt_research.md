# sources/distributed-fs/xrootd/src/XrdFfs/CMakeLists.txt

## Purpose

This CMake file builds the XrdFfs shared library and conditionally builds the `xrootdfs` FUSE executable. XrdFfs is the C/C++ support layer that wraps XrdPosix operations, maintains directory/stat/write caches, and supplies the FUSE callbacks used by the mount tool.

## Important APIs, Types, and Functions

`add_library(XrdFfs SHARED ...)` includes the Dent, Fsinfo, Misc, Posix, Queue, and Wcache implementation/header pairs. The library links privately to `XrdCl`, `XrdPosix`, `XrdUtils`, and pthread libraries. `set_target_properties()` applies XRootD's shared-library versioning.

When `ENABLE_FUSE` is true and the system is Linux or kFreeBSD, the script locates FUSE, sets `BUILD_FUSE`, adds `xrootdfs` from `XrdFfsXrootdfs.cc`, links it to `XrdFfs`, `XrdPosix`, FUSE, and pthreads, and installs both library and executable.

## Control Flow

The library is always declared. The executable branch returns early when FUSE is requested but not found without `FORCE_ENABLED`. With `FORCE_ENABLED`, missing FUSE is a configuration error.

## State and Persistence Behavior

The file does not persist runtime state. Build outputs are shared-library and executable artifacts installed under `${CMAKE_INSTALL_LIBDIR}` and `${CMAKE_INSTALL_BINDIR}`.

## Dependencies and Integration Points

This integrates XrdFfs into the larger XRootD build and gates FUSE support by platform and dependency discovery. Consumers link to `XrdFfs`; end users run `xrootdfs`.

## Risks and Edge Cases

FUSE support is excluded on non-Linux/non-kFreeBSD platforms. A missing FUSE package silently skips the executable when not force-enabled, which can surprise users expecting `xrootdfs`. Header files are listed as sources for IDE visibility rather than compilation.

## Test Signals

Build tests should cover `ENABLE_FUSE=ON/OFF`, missing FUSE with and without `FORCE_ENABLED`, install layout, and successful link resolution against XrdCl, XrdPosix, XrdUtils, and pthreads.
