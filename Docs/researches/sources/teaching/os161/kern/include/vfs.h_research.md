# File Research: sources/teaching/os161/kern/include/vfs.h

Publishes the Virtual File System interface. Low-level calls manage current directories, sync, root lookup, and device-name lookup. Mid-level calls perform full-path lookup and parent lookup. High-level pathname calls implement open, close, readlink, symlink, mkdir, link, remove, rmdir, rename, chdir, and getcwd.

The header also declares VFS bootstrap, boot filesystem management, device/filesystem registration, mount/unmount, swap attach/detach, and unmount-all. It defines a vnode array type and exposes the global `vfs_biglock` API.

The comments explicitly mark the big lock as a teaching simplification to remove for the filesystem assignment. Most functions accept mutable path buffers because lookup may destructively parse them.
