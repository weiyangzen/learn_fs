# File Research: sources/os/linux/linux/fs/notify/fsnotify.h

## Role

This private header defines fsnotify connector accessors and internal declarations shared by fsnotify implementation files.

## Connectors

`fsnotify_connp_t` is an RCU pointer to a `struct fsnotify_mark_connector`, embedded in watchable objects.

The header provides typed accessors for connector objects:

- inode
- mount
- superblock
- mount namespace

It also maps object type to superblock and retrieves the superblock mark pointer.

## Internal APIs

The header declares:

- notification queue flushing
- global SRCU object for mark traversal
- group priority comparison
- unmount inode cleanup
- connector-based mark destruction
- object-specific mark clearing helpers
- child dentry flag updates
- connector cache initialization

## Design Notes

This file isolates the internal connector abstraction from public fsnotify headers. Callers can clear marks by object type without knowing connector list internals.
