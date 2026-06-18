# sources/user-network-fs/mergerfs/src/xattr.hpp

## Purpose
Centralizes extended attribute feature detection and fallback constants.

## Important APIs, Types, and Functions
When `USE_XATTR` is defined on Linux, it includes `<sys/xattr.h>`. On non-Linux platforms it undefines `USE_XATTR` and emits a pragma message. It defines `XATTR_CREATE` and `XATTR_REPLACE` fallback values if missing.

## Control Flow
All logic is preprocessor-time platform selection.

## State and Persistence Behavior
No runtime state. It controls whether xattr-related code compiles.

## Dependencies and Integration Points
Used by xattr FUSE operations and tests covering `user.mergerfs.*` and POSIX xattrs.

## Risks and Edge Cases
Fallback flag values must match platform ABI expectations. Disabling xattrs at compile time changes user-visible behavior.

## Test Signals
Compile with and without `USE_XATTR`, run xattr mode tests, and verify create/replace flag behavior.
