# sources/user-network-fs/nfs-utils/support/include/nfs_paths.h

## Purpose
Defines fallback paths and lock/temp names for the mounted filesystem table.

## Important APIs, Types, and Functions
Defines `_PATH_MOUNTED`, `MOUNTED_LOCK`, and `MOUNTED_TEMP`.

## Control Flow
Mount helpers use these names when updating mounted table state.

## State and Persistence Behavior
No runtime state. Constants refer to persistent files.

## Dependencies and Integration Points
Included by mount support code where system path macros may be absent.

## Risks and Edge Cases
Defaulting `_PATH_MOUNTED` to `/etc/fstab` is unusual for mounted-state updates and depends on surrounding code expectations.

## Test Signals
Build mount utilities and verify configured path macros override these fallbacks.
