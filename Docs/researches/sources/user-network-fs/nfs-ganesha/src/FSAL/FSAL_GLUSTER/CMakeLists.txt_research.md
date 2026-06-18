# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/CMakeLists.txt

## Purpose

`CMakeLists.txt` defines the build target for the Gluster FSAL module. It sets GFAPI-related compile definitions, enumerates source files, creates the `fsalgluster` module library, links it to Ganesha and Gluster dependencies, assigns shared-object version properties, and installs it in the FSAL destination. The complete 60-line file was read for this report.

## Important APIs, Types, and Functions

Build-level items include `add_definitions(-D__USE_GNU ${GFAPI_CFLAGS})`, `fsalgluster_LIB_SRCS`, `add_library(fsalgluster MODULE ...)`, `add_sanitizers(fsalgluster)`, `target_link_libraries`, `set_target_properties`, and `install(TARGETS fsalgluster ...)`.

## Control Flow

CMake configures a module target from `main.c`, `export.c`, `handle.c`, `fsal_up.c`, `gluster_internal.h`, `gluster_internal.c`, `mds.c`, and `ds.c`. It links the target against `ganesha_nfsd`, system libraries, GFAPI libraries, LTTng libraries, and undefined-symbol rejection flags.

## State and Persistence Behavior

There is no runtime state. The file persists build/install contract: the output is a module named `fsalgluster` with version `4.2.0`, soversion `4`, installed under `${FSAL_DESTINATION}`.

## Dependencies and Integration Points

It integrates CMake feature detection variables (`GFAPI_CFLAGS`, `GFAPI_LIBRARIES`, `LTTNG_LIBRARIES`, `SYSTEM_LIBRARIES`, `LDFLAG_DISALLOW_UNDEF`, `FSAL_DESTINATION`) with the Gluster FSAL source set. Sanitizer integration is inherited through `add_sanitizers`.

## Risks and Edge Cases

The source list must stay synchronized with feature code; missing `mds.c`/`ds.c` would silently break pNFS support, while missing `fsal_up.c` would break upcalls. `-D__USE_GNU` can affect libc feature exposure globally for this target. `LIB_PREFIX` is set but not used locally. Link failures are a useful signal because `LDFLAG_DISALLOW_UNDEF` should catch missing GFAPI symbols.

## Test Signals

Test signals are a clean build with Gluster enabled, sanitizer builds, install packaging checks for `fsalgluster`, link checks with and without LTTng, GFAPI version compatibility builds, and pNFS/upcall symbol resolution.
