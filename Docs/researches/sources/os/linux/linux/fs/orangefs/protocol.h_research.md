# File Research: sources/os/linux/linux/fs/orangefs/protocol.h

## Role

Defines the kernel-side OrangeFS protocol ABI constants, object identifiers, attribute structures, ioctl command numbers, xattr limits, error encoding bits, and debug macros used by the OrangeFS client module.

## Main Contents

- `struct orangefs_khandle` is a 16-byte aligned handle. Comments explain compatibility with older 64-bit and newer 128-bit handle formats.
- `struct orangefs_object_kref` combines a kernel handle and filesystem ID.
- Inline handle helpers compare, export, and import fixed 16-byte handles.
- Error encoding constants define OrangeFS error bit layout and protocol-specific errors such as `ORANGEFS_ECANCEL`.
- Permission, inode flag, iteration token, attribute mask, xattr size, and name-size constants define the protocol limits used by upcall/downcall structures.
- `enum ORANGEFS_io_type` and `enum orangefs_ds_type` describe I/O direction and OrangeFS object kinds.
- `struct ORANGEFS_keyval_pair` and `struct ORANGEFS_sys_attr_s` define xattr and file metadata payloads.
- Device ioctl command numbers define the `/dev/orangefs` userspace interface.
- `struct ORANGEFS_dev_map_desc` is explicitly documented as needing 32-bit compatibility handling.
- `gossip_debug` and `gossip_err` provide lightweight debug/error logging wrappers.

## ABI and Compatibility Notes

The file uses fixed-width integer types and padding-oriented comments because the OrangeFS kernel module communicates with a userspace client process. Several comments explicitly warn about 32-bit userspace on 64-bit kernels and retaining field sizes or alignment.

## Dependencies

Includes Linux kernel, type, spinlock, slab, and ioctl headers, plus `orangefs-debug.h`.

## Research Notes

This is a protocol boundary file. Seemingly simple changes to field order, sizes, limits, or ioctl encodings would affect userspace client compatibility.
