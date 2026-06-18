# File Research: sources/teaching/os161/kern/vfs/vfslookup.c

Implements pathname translation entry points. A static `bootfs_vnode` anchors absolute paths beginning with `/`. `vfs_setbootfs` normalizes a filesystem name to include a trailing colon, changes to it, gets the resulting current directory, and installs it as bootfs under the VFS big lock. `vfs_clearbootfs` drops that reference.

The internal `getdevice` destructively parses a path into a starting vnode and remaining subpath. It handles relative paths via current directory, `device:path` via `vfs_getroot`, `/path` via bootfs, and `:path` via the root of the current filesystem.

`vfs_lookup` and `vfs_lookparent` hold `vfs_biglock`, call `getdevice`, dispatch to `VOP_LOOKUP` or `VOP_LOOKPARENT`, and balance references.
