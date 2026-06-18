# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/utilities.c

## Purpose

Provides `blockcheck()`, a device-name resolver used by UFS fsck-derived tools. It maps user input to a usable block or character device path when possible.

## Main Behavior

- Accepts an original filesystem/device name.
- If the path cannot be `stat()`ed and has no slash, retries under `/dev`.
- If the path is a character or block device, returns that path.
- If the path is a directory, removes a trailing slash, consults `getfsfile()`, and retries using the fstab device spec.
- If resolution fails or the target is not a device, returns the original name and leaves the caller/user to decide.

## Integration Points

Includes `fsck.h` and is shared by fsck-derived UFS utilities. Uses libc/fstab APIs and `_PATH_DEV`.

## Risk Notes

The function mutates `origname` to remove a trailing slash when resolving directories. It returns a static buffer for `/dev/<name>` expansion, so callers must not expect stable contents across repeated calls.
