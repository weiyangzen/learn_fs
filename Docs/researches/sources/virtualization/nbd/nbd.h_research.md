# File Research: sources/virtualization/nbd/nbd.h

## Purpose
Defines userspace-visible NBD protocol constants, ioctl numbers, command codes, feature flags, packet structures, structured-reply types, and protocol error constants.

## Main Contents
- Linux NBD ioctl macros such as `NBD_SET_SOCK`, `NBD_DO_IT`, `NBD_DISCONNECT`, and `NBD_SET_FLAGS`.
- Command enum values for READ, WRITE, DISC, FLUSH, TRIM, CACHE, WRITE_ZEROES, BLOCK_STATUS, and RESIZE.
- Command flag masks for FUA, NO_HOLE, and DF.
- Export/server flags such as read-only, flush/FUA/trim/write-zeroes support, DF support, and multi-connection safety.
- Wire magic values for requests, replies, structured replies, option replies, and transaction logs.
- Packed wire structs: `nbd_request`, `nbd_reply`, `nbd_structured_reply`, and `nbd_structured_error_payload`.

## Dependencies
Requires fixed-width integer types to be available before inclusion. The ioctl macros assume `_IO` is defined by platform ioctl headers when used.

## Risks and Notes
The packed wire structs are central ABI definitions; callers must explicitly convert every multibyte field to or from network byte order. The header intentionally omits kernel-only `nbd_device` details.
