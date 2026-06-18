# sources/sync-backup/casync/src/chattr.c

## Purpose

`chattr.c` wraps Linux filesystem attribute ioctls for generic `FS_IOC_*FLAGS` attributes and FAT-specific attributes. It normalizes unsupported filesystems/node types so reading unsupported attributes yields zero and writing zero attributes succeeds.

## Important APIs, Types, and Functions

`read_attr_fd()` calls `ioctl(fd, FS_IOC_GETFLAGS, ret)` and returns `1` when supported, `0` with `*ret = 0` when unsupported, or negative errno. `write_attr_fd()` calls `FS_IOC_SETFLAGS`; unsupported zero writes return `0`, other failures are negative errno, and supported writes return `1`. `mask_attr_fd()` reads current flags, merges `(old & ~mask) | (value & mask)`, and writes only if changed.

`read_fat_attr_fd()`, `write_fat_attr_fd()`, and `mask_fat_attr_fd()` provide the same pattern for `FAT_IOCTL_GET_ATTRIBUTES` and `FAT_IOCTL_SET_ATTRIBUTES` using `uint32_t`.

## Control Flow

The mask functions are read-modify-write helpers with a fast path for `mask == 0` and no-op when computed attributes match existing attributes. Unsupported handling is centralized in the read/write helpers through `ERRNO_IS_UNSUPPORTED()`.

## State and Persistence Behavior

The only persistent behavior is kernel-level mutation of inode/FAT attributes through ioctls. No process-global state is stored.

## Dependencies and Integration Points

The file includes Linux ioctl definitions and `util.h` for `ERRNO_IS_UNSUPPORTED()`. It integrates with encoder/decoder metadata preservation for chattr and FAT attributes.

## Risks and Edge Cases

Unsupported filesystems are silently treated as zero attributes, which is intentional but can hide missing metadata preservation. Writes of nonzero attributes to unsupported filesystems fail. Race conditions are possible between read and masked write if attributes change concurrently. The functions assert valid fds/ret pointers instead of returning errors for those programming mistakes.

## Test Signals

Tests should cover supported filesystems when available, unsupported node types/filesystems, writing zero to unsupported targets, writing nonzero unsupported attributes, mask no-op, mask changed value, and FAT-specific paths if the test environment can mount or mock FAT ioctl behavior.
