# sources/user-network-fs/nfs-utils/support/include/xmalloc.h

## Purpose
Compatibility wrapper that exposes checked allocation declarations from `xcommon.h`.

## Important APIs, Types, and Functions
Includes `xcommon.h`; no independent API.

## Control Flow
Including this file gives callers `xmalloc`, `xstrdup`, and related helpers.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by older code that expects an `xmalloc.h` header.

## Risks and Edge Cases
Any include-cycle or guard issue is inherited from `xcommon.h`.

## Test Signals
Compile sources that include `xmalloc.h` directly.
