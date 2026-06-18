# File Research: sources/os/linux/linux/fs/notify/fdinfo.c

## Role

This file implements `/proc/<pid>/fdinfo` output for inotify and fanotify descriptors when procfs is enabled.

It walks a group's marks under `fsnotify_group_lock()` and prints per-mark state in a userspace-debuggable format.

## Shared Logic

`show_fdinfo()` gets the fsnotify group from `file->private_data`, locks the group, iterates `group->marks_list`, invokes a subsystem-specific printer, and stops if the seq buffer overflows.

When exportfs is enabled, `show_mark_fhandle()` tries to encode an inode file handle under a shared superblock lock and prints handle bytes, type, and hex payload.

## Inotify Output

For inode marks, `inotify_fdinfo()` prints:

- watch descriptor
- inode number
- superblock device
- userspace mask
- ignored mask placeholder
- optional encoded file handle

It grabs the inode with `igrab()` and releases it with `iput()`.

## Fanotify Output

`fanotify_show_fdinfo()` first prints fanotify init flags and event open flags. Per-mark output varies by connector type:

- inode: inode number, device, mark flags, mask, ignore mask, optional handle
- vfsmount: mount id, mark flags, mask, ignore mask
- superblock: device, mark flags, mask, ignore mask
- mount namespace: namespace inode number, mark flags, mask, ignore mask

## Design Notes

The file is intentionally diagnostic. It avoids creating references unless needed and tolerates objects disappearing by using connector type checks and reference helpers.
