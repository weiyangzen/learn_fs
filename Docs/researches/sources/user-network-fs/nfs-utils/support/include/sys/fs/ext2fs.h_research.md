# sources/user-network-fs/nfs-utils/support/include/sys/fs/ext2fs.h

## Purpose
Provides compatibility ext2 filesystem ioctl and mount flag constants for platforms lacking this header.

## Important APIs, Types, and Functions
`EXT2_IOC_*`, filesystem state flags, mount option flags, helper macros `clear_opt`, `set_opt`, `test_opt`, and default mount-count/check intervals.

## Control Flow
Consumers use constants in ioctl or option manipulation code; no executable flow is present here.

## State and Persistence Behavior
No state. Values represent filesystem/kernel ABI constants.

## Dependencies and Integration Points
Included by filesystem/mount support code when ext2 flag definitions are needed.

## Risks and Edge Cases
Macros assume an ext2-style superblock layout for `test_opt`. Kernel header drift can make compatibility constants stale.

## Test Signals
Compile mount/filesystem utilities on systems without native ext2 headers and test ioctl flag get/set where supported.
