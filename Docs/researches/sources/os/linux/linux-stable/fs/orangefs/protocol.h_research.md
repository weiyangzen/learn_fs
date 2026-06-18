# File Research: sources/os/linux/linux-stable/fs/orangefs/protocol.h

## Scope

This header defines OrangeFS kernel/userspace protocol primitives, object handles, object references, attribute masks and structures, permission bits, xattr limits, OrangeFS-specific errors, device ioctl numbers, userspace protocol version requirements, shared device-map descriptors, and debug logging macros.

## APIs And Constants

- Object identifiers: `struct orangefs_khandle`, `struct orangefs_object_kref`, `ORANGEFS_khandle_cmp()`, `ORANGEFS_khandle_to()`, and `ORANGEFS_khandle_from()`.
- Filesystem and protocol constants: `ORANGEFS_SUPER_MAGIC`, `ORANGEFS_KERNEL_PROTO_VERSION`, `ORANGEFS_MINIMUM_USERSPACE_VERSION`, and `ORANGEFS_FS_ID_NULL`.
- Error encoding bits: `ORANGEFS_ERROR_BIT`, `ORANGEFS_NON_ERRNO_ERROR_BIT`, `ORANGEFS_ERROR_CLASS_BITS`, `ORANGEFS_ERROR_NUMBER_BITS`, and OrangeFS protocol errors such as `ORANGEFS_ECANCEL`.
- Permission and attribute masks: OrangeFS owner/group/other permission bits, immutable/append/noatime flags, `ORANGEFS_ATTR_SYS_*`, and aggregate masks.
- Xattr limits and flags: `ORANGEFS_MAX_XATTR_NAMELEN`, `ORANGEFS_MAX_XATTR_VALUELEN`, `ORANGEFS_MAX_XATTR_LISTLEN`, `ORANGEFS_XATTR_CREATE`, and `ORANGEFS_XATTR_REPLACE`.
- Data model types: `enum ORANGEFS_io_type`, `enum orangefs_ds_type`, `struct ORANGEFS_keyval_pair`, and `struct ORANGEFS_sys_attr_s`.
- Device interface: `ORANGEFS_DEV_*` ioctl numbers, debug mask structs, and `struct ORANGEFS_dev_map_desc`.
- Declares `ORANGEFS_util_translate_mode()` and exposes `gossip_debug()` / `gossip_err`.

## Control Flow And Behavior

- Handle comparison walks bytes from high to low and assumes little-endian handle ordering.
- Handle export/import helpers always copy the 16-byte kernel handle and zero-pad the destination buffer beyond the handle size.
- `ORANGEFS_sys_attr_s` is the central attribute carrier for getattr, setattr, create, mkdir, symlink, and copy-up-style metadata exchanges with userspace.
- Device ioctl constants define the ABI used by the OrangeFS character-device path for mapping shared buffers, remounting, debug configuration, version negotiation, and client strings.

## State And Data Structures

- `struct orangefs_khandle` is 16 bytes and aligned to 8 bytes.
- `struct orangefs_object_kref` combines a handle with a signed 32-bit fs id and padding.
- `struct ORANGEFS_keyval_pair` embeds fixed-size key/value xattr buffers.
- `struct ORANGEFS_sys_attr_s` includes ownership, permissions, times, size, optional allocated strings, distributed directory hints, mirror count, object type, flags, mask, and block size.
- Device-map descriptors retain pointer/size/count fields and must be normalized for 32-bit userspace compatibility.

## Dependencies

- Includes Linux kernel types, ioctl helpers, slab declarations, spinlock types, and `orangefs-debug.h`.
- The constants are consumed by OrangeFS superblock, inode, directory, xattr, waitqueue, and device protocol code.

## Risks And Invariants

- This is a kernel/userspace ABI header; structure sizes, padding, fixed buffer lengths, and ioctl numbers must remain compatible with OrangeFS client-core.
- Xattr name/value/list limits intentionally differ from generic Linux xattr limits and are tied to OrangeFS protocol request buffers.
- Error-code bit layout is decoded by `orangefs_normalize_to_errno()`; changes must stay synchronized with server-side encoding.
