# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindNfsIdmap.cmake

## Purpose

`FindNfsIdmap.cmake` locates libnfsidmap headers and library for NFS identity mapping support.

## Important APIs, Types, and Functions

The module sets `NFSIDMAP_INCLUDE_DIR`, `NFSIDMAP_LIBRARY`, and `NFSIDMAP_FOUND` using `FIND_PATH` and `FIND_LIBRARY`. It emits status or fatal messages based on `NFSIDMAP_FIND_QUIETLY` and `NfsIdmap_FIND_REQUIRED`.

## Control Flow

Configure searches for `nfsidmap.h` and `libnfsidmap`. If both are present, `NFSIDMAP_FOUND` becomes true and a status message is emitted unless quiet. If either is missing and the package is required, configuration aborts.

## State and Persistence Behavior

Only CMake variables are mutated. There is no target creation or generated output.

## Dependencies and Integration Points

The result feeds build paths that need NFSv4 name-to-id mapping. It depends on libnfsidmap development packaging.

## Risks and Edge Cases

The module does not use `FindPackageHandleStandardArgs`, does not mark variables advanced, and has inconsistent package-name casing in required checks. It does not verify any symbols or version, so a stale incompatible library could pass discovery.

## Test Signals

Configure runs with and without `libnfsidmap-devel` validate required/optional behavior. Compile and link of idmapping code is needed to catch header/library ABI mismatches.
