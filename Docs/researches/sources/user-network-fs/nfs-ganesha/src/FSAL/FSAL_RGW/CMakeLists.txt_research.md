# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/CMakeLists.txt

## Purpose
Builds and installs the RGW FSAL module for Ceph RADOS Gateway integration.

## Important APIs, Types, and Functions
Defines `fsalrgw_LIB_SRCS`, includes `${RGW_INCLUDE_DIR}`, builds MODULE library `fsalrgw`, links Ganesha, RGW, system libraries, and disallow-undefined flags, then installs to `${FSAL_DESTINATION}`.

## Control Flow
Adds `_FILE_OFFSET_BITS=64`, compiles RGW sources, applies sanitizers, links the loadable module, sets version `4.2.0`, and installs it.

## State and Persistence Behavior
No runtime state; build/install only.

## Dependencies and Integration Points
Depends on RGW headers/libraries, `ganesha_nfsd`, system libs, and FSAL destination settings.

## Risks
Ceph RGW API/version mismatch will fail compile/link, with additional checks in `internal.h`. Undefined symbols are disallowed.

## Test Signals
Configure output for RGW include dir, successful module link, and installed `fsalrgw`.
