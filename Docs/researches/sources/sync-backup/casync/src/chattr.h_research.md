# sources/sync-backup/casync/src/chattr.h

## Purpose

`chattr.h` declares Linux attribute ioctl wrappers for generic and FAT filesystem attributes.

## Important APIs, Types, and Functions

The header exposes `read_attr_fd()`, `write_attr_fd()`, `mask_attr_fd()`, `read_fat_attr_fd()`, `write_fat_attr_fd()`, and `mask_fat_attr_fd()`. It includes `<inttypes.h>` for `uint32_t`.

## Control Flow

Callers typically read attributes during encoding, write attributes during decoding, or use mask functions when applying only a subset of preserved flags.

## State and Persistence Behavior

The API operates on caller-provided file descriptors and persists changes through kernel ioctls.

## Dependencies and Integration Points

This header is consumed by archive encoder/decoder metadata code. It hides Linux ioctl details behind errno-style helper functions.

## Risks and Edge Cases

The implementation is Linux-specific. Callers need to understand that `0` means unsupported/no-op and `1` means supported/action, not simple boolean success.

## Test Signals

API tests should validate return-value interpretation and build behavior on Linux configurations with the expected ioctl constants.
