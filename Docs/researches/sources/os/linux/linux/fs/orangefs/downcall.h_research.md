# File Research: sources/os/linux/linux/fs/orangefs/downcall.h

Defines kernel-facing response structures sent from OrangeFS userspace daemon to the kernel.

Contents:
- Response payloads for I/O, lookup, create, symlink, getattr, mkdir, statfs, mount, xattr get/list, parameter requests, performance counters, filesystem keys, and feature negotiation.
- `orangefs_downcall_s` wraps operation type, status, optional trailer size/buffer, and a union of response payloads.
- `orangefs_readdir_response_s` defines the header stored at the beginning of readdir trailers.

Important role:
- This header is included by the device protocol and determines the ABI layout copied through `/dev/pvfs2-req`.
