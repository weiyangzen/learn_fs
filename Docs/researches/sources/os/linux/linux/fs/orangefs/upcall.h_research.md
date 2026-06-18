# File Research: sources/os/linux/linux/fs/orangefs/upcall.h

## Role

Defines all OrangeFS kernel-to-userspace upcall request payload structures and the top-level `orangefs_upcall_s` union.

## Main Contents

The file declares request structures for:

- File I/O, lookup, create, symlink, getattr, setattr, remove, mkdir.
- Readdir and readdirplus.
- Rename, statfs, truncate, readahead cache flush.
- Filesystem mount and unmount.
- Xattr get/set/list/remove.
- Operation cancel and fsync.
- Parameter get/set requests, performance count requests, fs-key requests, and feature negotiation.

`struct orangefs_upcall_s` carries operation type, uid/gid, pid/tgid, retained trailer fields for compatibility, and a tagged request union.

## ABI and Compatibility Notes

The header is explicitly “sanitized” for 32/64-bit client-core interaction. Many structures include padding fields and use fixed-width types to preserve layout for userspace communication.

## Dependencies

Depends on protocol-level types such as `orangefs_object_kref`, `ORANGEFS_sys_attr_s`, `ORANGEFS_keyval_pair`, and OrangeFS constants.

## Research Notes

This is a strict ABI surface. Adding a request type or changing request layout requires matching userspace client support and downcall handling.
