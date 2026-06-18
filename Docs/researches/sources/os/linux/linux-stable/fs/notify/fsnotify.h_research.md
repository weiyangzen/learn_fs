# File Research: sources/os/linux/linux-stable/fs/notify/fsnotify.h

## Summary
Internal fsnotify header for connector accessors, mark cleanup helpers, SRCU state, group comparison, and connector cache initialization.

## Contents
Defines `fsnotify_connp_t`, typed connector-to-object helpers for inode, mount, superblock, and mount namespace, object-to-superblock helpers, and inline clear-mark helpers for each object type.

## Important Details
The header exposes `fsnotify_mark_srcu`, `fsnotify_compare_groups()`, `fsnotify_unmount_inodes()`, `fsnotify_destroy_marks()`, and `fsnotify_set_children_dentry_flags()`. Superblock marks are reached through optional `fsnotify_sb_info`.

## Risks
These helpers encode the connector object model used by `mark.c` and `fsnotify.c`. Incorrect object type handling can corrupt mark lists or miss cleanup during inode eviction, mount teardown, superblock shutdown, or namespace destruction.
