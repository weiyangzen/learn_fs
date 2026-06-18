# File Research: sources/os/linux/linux/fs/nsfs.c

## Role

This file implements `nsfs`, the pseudo filesystem used to represent Linux namespaces as file objects. It supports namespace file opening, proc namespace paths, namespace ioctls, exportable file handles, and namespace active-reference helpers.

## Namespace Paths And Files

`nsfs_get_root()` returns the nsfs root path. `ns_get_path_cb()` and `ns_get_path()` construct paths from stashed namespace dentries. `open_namespace_file()` and `open_namespace()` open namespace file objects and consume namespace references.

Dentries use dynamic names like `mnt:[ino]` or `net:[ino]`.

Inode eviction drops the active namespace reference and calls the namespace operation `put()`.

## Ioctls

`ns_ioctl()` implements namespace fd operations including:

- get owning user namespace
- get parent namespace
- get namespace type
- get owner uid for user namespaces
- translate pids/tgids into or out of pid namespaces
- get namespace id
- get mount namespace id
- extensible mount namespace info
- get next/previous mount namespace fd and optional info

Validation separates known fixed ioctls from extensible mount namespace ioctls. Sequential mount namespace traversal requires permission to see all namespaces.

## Mount Namespace Info

`copy_ns_info_to_user()` supports extensible struct sizing. It fills known fields and copies only the size supported by both userspace and kernel.

## Exportfs Support

`nsfs_encode_fh()` encodes namespace id, type, and inode number into an nsfs file handle.

`nsfs_fh_to_dentry()` decodes handles through namespace-tree lookup, validates trailing bytes and type fields, checks namespace visibility/security, resurrects stashed namespace dentries when allowed, and returns the dentry.

Export operations also define open and permission hooks.

## Pseudo Filesystem Setup

`nsfs_init_fs_context()` initializes a pseudo fs with nsfs super operations, export operations, dentry operations, and stashed operations. `nsfs_init()` mounts it internally and clears `SB_NOUSER` so it can be exposed.

## Active Reference Helpers

`nsproxy_ns_active_get()` and `nsproxy_ns_active_put()` adjust active references for all namespaces contained in an nsproxy.

## Design Notes

nsfs is both a proc-facing namespace fd filesystem and an exportable object namespace. The stashed dentry design lets namespace objects reappear as files when later referenced by sockets, ioctls, or handles.
